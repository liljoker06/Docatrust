const express = require("express");
const {
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
} = require("../controllers/admin.controller.js");

const adminRouter = express.Router();

// Stats
adminRouter.get("/stats", getStats);

// Users
adminRouter.get("/users", listUsers);
adminRouter.patch("/users/:id/role", updateUserRole);
adminRouter.patch("/users/:id/disable", disableUser);
adminRouter.delete("/users/:id", deleteUser);

// Documents
adminRouter.get("/documents", listAllDocuments);
adminRouter.get("/documents/:id", getDocumentDetails);

// Alerts
adminRouter.get("/alerts", listAlerts);
adminRouter.patch("/alerts/:id/resolve", resolveAlert);

// Logs
adminRouter.get("/logs", listLogs);

module.exports = adminRouter;
