const asyncHandler = require("../utils/asynchandler.util");
const { User, Token } = require("../models/index");

const VALID_ROLES = ["ADMIN", "OPERATOR", "AUDITOR"];




const listUsers = asyncHandler(async (req, res) => {
  const users = await User.findAll({
    attributes: { exclude: ["password_hash"] },
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
  if (!user) {
    return res.status(404).json({ error: true, message: "User not found" });
  }

  await user.update({ role });
  return res.status(200).json({ error: false, user: { id: user.id, email: user.email, role: user.role } });
});




const disableUser = asyncHandler(async (req, res) => {
  const { id } = req.params;

  if (id === req.user.id) {
    return res.status(400).json({ error: true, message: "Cannot disable your own account" });
  }

  const user = await User.findByPk(id);
  if (!user) {
    return res.status(404).json({ error: true, message: "User not found" });
  }

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
  if (!user) {
    return res.status(404).json({ error: true, message: "User not found" });
  }

  await user.destroy();
  return res.status(200).json({ error: false, message: "User deleted" });
});

module.exports = { listUsers, updateUserRole, disableUser, deleteUser };

