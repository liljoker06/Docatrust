const express = require("express");

const authMiddleware = require("../middlewares/auth.middleware");
const upload = require("../config/upload");
const {
  uploadDocument,
  listDocuments,
  getDocumentStatus,
  getDocumentResult,
  downloadDocument,
} = require("../controllers/document.controller");

const documentRouter = express.Router();

documentRouter.post("/upload",                  authMiddleware, upload.single("file"), uploadDocument);
documentRouter.get("/",                         authMiddleware, listDocuments);
documentRouter.get("/:documentId/status",       authMiddleware, getDocumentStatus);
documentRouter.get("/:documentId/result",       authMiddleware, getDocumentResult);
documentRouter.get("/:documentId/download",     authMiddleware, downloadDocument);

module.exports = documentRouter;
