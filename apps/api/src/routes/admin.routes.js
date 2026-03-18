const express = require("express");
const requireRole = require("../middlewares/role.middleware.js");
const { listUsers, updateUserRole, disableUser, deleteUser } = require("../controllers/admin.controller.js");

const adminRouter = express.Router();

adminRouter.get("/users", listUsers);
adminRouter.patch("/users/:id/role", updateUserRole);
adminRouter.patch("/users/:id/disable", disableUser);
adminRouter.delete("/users/:id", deleteUser);

module.exports = adminRouter;
