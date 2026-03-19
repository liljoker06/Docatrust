const multer = require("multer");

const ALLOWED_MIME_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/tiff",
];

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 20 * 1024 * 1024 }, // 20 MB max
  fileFilter: (req, file, next) => {
    if (ALLOWED_MIME_TYPES.includes(file.mimetype)) {
      next(null, true);
    } else {
      next(
        new Error(
          "Type de fichier non autorisé. Formats acceptés : PDF, JPEG, PNG, TIFF."
        )
      );
    }
  },
});

module.exports = upload;
