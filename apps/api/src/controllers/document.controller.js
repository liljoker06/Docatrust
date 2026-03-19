const crypto = require("crypto");
const { v4: generateUuid } = require("uuid");
const axios = require("axios");

const asyncHandler = require("../utils/asynchandler.util");
const { MinioObject, DocumentRaw, PipelineLog } = require("../models");
const minioClient = require("../config/minio");

const RAW_BUCKET     = process.env.MINIO_BUCKET_RAW     || "raw";
const CLEAN_BUCKET   = process.env.MINIO_BUCKET_CLEAN   || "clean";
const CURATED_BUCKET = process.env.MINIO_BUCKET_CURATED || "curated";

const AIRFLOW_BASE_URL = process.env.AIRFLOW_URL    || "http://airflow-webserver:8080";
const AIRFLOW_DAG_ID   = "document_pipeline";

// ─── Upload ────────────────────────────────────────────────────────────────

const uploadDocument = asyncHandler(async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: true, message: "No file provided." });
  }

  const uploadedFile   = req.file;
  const documentId     = generateUuid();
  const objectKey      = `uploads/${documentId}/${uploadedFile.originalname}`;
  const checksumSha256 = crypto.createHash("sha256").update(uploadedFile.buffer).digest("hex");

  await minioClient.putObject(
    RAW_BUCKET, objectKey,
    uploadedFile.buffer, uploadedFile.size,
    { "Content-Type": uploadedFile.mimetype }
  );

  const minioRecord = await MinioObject.create({
    bucket_name:       RAW_BUCKET,
    zone:              "RAW",
    object_key:        objectKey,
    original_filename: uploadedFile.originalname,
    mime_type:         uploadedFile.mimetype,
    size_bytes:        uploadedFile.size,
    checksum_sha256:   checksumSha256,
    is_encrypted:      false,
  });

  await DocumentRaw.create({
    id:              documentId,
    uploader_id:     req.user.id,
    minio_object_id: minioRecord.id,
    status:          "RAW",
  });

  await PipelineLog.create({
    document_id: documentId,
    to_status:   "RAW",
    status:      "SUCCESS",
  });

  await triggerAirflowPipeline(documentId, objectKey, req.user.id);

  return res.status(201).json({
    error:       false,
    status:      "pending",
    document_id: documentId,
  });
});

// ─── Liste des documents ───────────────────────────────────────────────────

const listDocuments = asyncHandler(async (req, res) => {
  const userDocuments = await DocumentRaw.findAll({
    where:   { uploader_id: req.user.id },
    include: [{ model: MinioObject, as: "minioRaw" }],
    order:   [["created_at", "DESC"]],
  });

  return res.status(200).json({ error: false, documents: userDocuments });
});

// ─── Statut d'un document ──────────────────────────────────────────────────

const getDocumentStatus = asyncHandler(async (req, res) => {
  const { documentId } = req.params;

  const document = await DocumentRaw.findByPk(documentId);
  if (!document) {
    return res.status(404).json({ error: true, message: "Document not found." });
  }

  const latestLog = await PipelineLog.findOne({
    where: { document_id: documentId },
    order: [["created_at", "DESC"]],
  });

  return res.status(200).json({
    error:       false,
    document_id: documentId,
    status:      document.status,
    latest_log:  latestLog,
  });
});

// ─── Résultat OCR depuis MinIO ─────────────────────────────────────────────

const getDocumentResult = asyncHandler(async (req, res) => {
  const { documentId } = req.params;

  const document = await DocumentRaw.findByPk(documentId);
  if (!document) {
    return res.status(404).json({ error: true, message: "Document not found." });
  }

  let result = null;
  let zone   = null;

  if (document.status === "CURATED") {
    try {
      const stream = await minioClient.getObject(CURATED_BUCKET, `processed/${documentId}/curated.json`);
      result = await streamToJson(stream);
      zone   = "curated";
    } catch {}
  }

  if (!result && ["CURATED", "CLEAN"].includes(document.status)) {
    try {
      const stream = await minioClient.getObject(CLEAN_BUCKET, `processed/${documentId}/ocr_result.json`);
      result = await streamToJson(stream);
      zone   = "clean";
    } catch {}
  }

  if (!result) {
    return res.status(404).json({ error: true, message: "Résultats pas encore disponibles." });
  }

  return res.status(200).json({
    error:       false,
    document_id: documentId,
    status:      document.status,
    zone,
    result,
  });
});

// ─── Téléchargement du fichier original ───────────────────────────────────

const downloadDocument = asyncHandler(async (req, res) => {
  const { documentId } = req.params;

  const document = await DocumentRaw.findByPk(documentId);
  if (!document) {
    return res.status(404).json({ error: true, message: "Document not found." });
  }

  const minioRecord = await MinioObject.findByPk(document.minio_object_id);
  if (!minioRecord) {
    return res.status(404).json({ error: true, message: "Fichier introuvable dans le stockage." });
  }

  const fileStream = await minioClient.getObject(RAW_BUCKET, minioRecord.object_key);
  res.setHeader("Content-Disposition", `attachment; filename="${minioRecord.original_filename}"`);
  res.setHeader("Content-Type", minioRecord.mime_type || "application/octet-stream");
  fileStream.pipe(res);
});

// ─── Helpers ───────────────────────────────────────────────────────────────

function streamToJson(stream) {
  return new Promise((resolve, reject) => {
    let rawData = "";
    stream.on("data",  (chunk) => { rawData += chunk; });
    stream.on("end",   () => { try { resolve(JSON.parse(rawData)); } catch (e) { reject(e); } });
    stream.on("error", reject);
  });
}

async function triggerAirflowPipeline(documentId, objectKey, uploaderId) {
  const airflowRunId = `upload_${documentId}`;
  try {
    await axios.post(
      `${AIRFLOW_BASE_URL}/api/v1/dags/${AIRFLOW_DAG_ID}/dagRuns`,
      {
        dag_run_id: airflowRunId,
        conf: { document_id: documentId, bucket: RAW_BUCKET, object_key: objectKey, uploader_id: uploaderId },
      },
      { auth: { username: process.env.AIRFLOW_USER, password: process.env.AIRFLOW_PASSWORD } }
    );
    await PipelineLog.create({
      document_id: documentId, from_status: "RAW", status: "SUCCESS",
      airflow_dag_id: AIRFLOW_DAG_ID, airflow_run_id: airflowRunId,
    });
  } catch (airflowError) {
    await PipelineLog.create({
      document_id: documentId, from_status: "RAW", status: "FAILURE",
      airflow_dag_id: AIRFLOW_DAG_ID, airflow_run_id: airflowRunId,
      error_message: airflowError.message,
    });
  }
}

module.exports = { uploadDocument, listDocuments, getDocumentStatus, getDocumentResult, downloadDocument };
