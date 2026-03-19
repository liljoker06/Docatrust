const asyncHandler = require("../utils/asynchandler.util");
const {
  User,
  Token,
  DocumentRaw,
  DocumentClean,
  DocumentCurated,
  MinioObject,
  PipelineLog,
  Inconsistency,
  ComplianceAlert,
} = require("../models/index");

const VALID_ROLES = ["ADMIN", "OPERATOR", "AUDITOR"];

// ─── USERS ───────────────────────────────────────────────────────────────────

const listUsers = asyncHandler(async (_req, res) => {
  const users = await User.findAll({
    attributes: { exclude: ["password_hash"] },
    order: [["created_at", "DESC"]],
  });
  return res.status(200).json({ error: false, users });
});

const updateUserRole = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { role } = req.body;

  if (!role || !VALID_ROLES.includes(role)) {
    return res.status(400).json({ error: true, message: `Role must be one of: ${VALID_ROLES.join(", ")}` });
  }

  const user = await User.findByPk(id);
  if (!user) return res.status(404).json({ error: true, message: "User not found" });

  await user.update({ role });
  return res.status(200).json({ error: false, user: { id: user.id, email: user.email, role: user.role } });
});

const disableUser = asyncHandler(async (req, res) => {
  const { id } = req.params;

  if (id === req.user.id) {
    return res.status(400).json({ error: true, message: "Cannot disable your own account" });
  }

  const user = await User.findByPk(id);
  if (!user) return res.status(404).json({ error: true, message: "User not found" });

  await user.update({ is_active: false });
  await Token.update({ is_revoked: true }, { where: { user_id: id, is_revoked: false } });

  return res.status(200).json({ error: false, message: "User disabled" });
});

const deleteUser = asyncHandler(async (req, res) => {
  const { id } = req.params;

  if (id === req.user.id) {
    return res.status(400).json({ error: true, message: "Cannot delete your own account" });
  }

  const user = await User.findByPk(id);
  if (!user) return res.status(404).json({ error: true, message: "User not found" });

  await user.destroy();
  return res.status(200).json({ error: false, message: "User deleted" });
});

// ─── STATS ────────────────────────────────────────────────────────────────────

const getStats = asyncHandler(async (_req, res) => {
  const [totalUsers, totalDocuments, rawDocs, cleanDocs, curatedDocs, errorDocs, openAlerts] =
    await Promise.all([
      User.count(),
      DocumentRaw.count(),
      DocumentRaw.count({ where: { status: "RAW" } }),
      DocumentRaw.count({ where: { status: "CLEAN" } }),
      DocumentRaw.count({ where: { status: "CURATED" } }),
      DocumentRaw.count({ where: { status: "ERROR" } }),
      ComplianceAlert.count({ where: { is_resolved: false } }),
    ]);

  return res.status(200).json({
    error: false,
    stats: {
      totalUsers,
      totalDocuments,
      docsByStatus: { RAW: rawDocs, CLEAN: cleanDocs, CURATED: curatedDocs, ERROR: errorDocs },
      openAlerts,
    },
  });
});

// ─── DOCUMENTS ────────────────────────────────────────────────────────────────

const listAllDocuments = asyncHandler(async (_req, res) => {
  const documents = await DocumentRaw.findAll({
    include: [
      { model: User, as: "uploader", attributes: ["id", "email", "role"] },
      { model: MinioObject, as: "minioRaw", attributes: ["original_filename", "mime_type", "size_bytes"] },
    ],
    order: [["created_at", "DESC"]],
  });
  return res.status(200).json({ error: false, documents });
});

const getDocumentDetails = asyncHandler(async (req, res) => {
  const { id } = req.params;

  const document = await DocumentRaw.findByPk(id, {
    include: [
      { model: User, as: "uploader", attributes: ["id", "email", "role"] },
      { model: MinioObject, as: "minioRaw" },
      {
        model: DocumentClean,
        include: [{ model: MinioObject, as: "minioClean", attributes: ["object_key"] }],
      },
      {
        model: DocumentCurated,
        include: [
          { model: MinioObject, as: "minioCurated", attributes: ["object_key"] },
          { model: Inconsistency },
        ],
      },
      { model: PipelineLog, order: [["created_at", "ASC"]] },
    ],
  });

  if (!document) return res.status(404).json({ error: true, message: "Document not found" });

  return res.status(200).json({ error: false, document });
});

// ─── ALERTS ───────────────────────────────────────────────────────────────────

const listAlerts = asyncHandler(async (_req, res) => {
  const alerts = await ComplianceAlert.findAll({
    include: [
      {
        model: Inconsistency,
        include: [
          {
            model: DocumentCurated,
            include: [
              {
                model: DocumentRaw,
                include: [
                  { model: MinioObject, as: "minioRaw", attributes: ["original_filename"] },
                  { model: User, as: "uploader", attributes: ["email"] },
                ],
              },
            ],
          },
        ],
      },
      { model: User, as: "assignee", attributes: ["id", "email"] },
    ],
    order: [["created_at", "DESC"]],
  });
  return res.status(200).json({ error: false, alerts });
});

const resolveAlert = asyncHandler(async (req, res) => {
  const { id } = req.params;

  const alert = await ComplianceAlert.findByPk(id);
  if (!alert) return res.status(404).json({ error: true, message: "Alert not found" });

  await alert.update({ is_resolved: true, resolved_at: new Date() });
  return res.status(200).json({ error: false, message: "Alert resolved" });
});

// ─── LOGS ────────────────────────────────────────────────────────────────────

const listLogs = asyncHandler(async (_req, res) => {
  const logs = await PipelineLog.findAll({
    include: [
      {
        model: DocumentRaw,
        include: [{ model: MinioObject, as: "minioRaw", attributes: ["original_filename"] }],
      },
    ],
    order: [["created_at", "DESC"]],
    limit: 200,
  });
  return res.status(200).json({ error: false, logs });
});

module.exports = {
  listUsers,
  updateUserRole,
  disableUser,
  deleteUser,
  getStats,
  listAllDocuments,
  getDocumentDetails,
  listAlerts,
  resolveAlert,
  listLogs,
};
