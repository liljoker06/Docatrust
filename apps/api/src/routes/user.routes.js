const express = require("express");
const authMiddleware = require("../middlewares/auth.middleware.js");
const { register, login, me } = require("../controllers/user.controller.js");

const userRouter = express.Router();

userRouter.post("/", register);
userRouter.post("/login", login);
userRouter.get("/me", authMiddleware, me);

module.exports = userRouter;
