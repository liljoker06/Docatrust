require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { sequelize } = require("./models");
const userRouter = require("./routes/user.routes.js");
const adminRouter = require("./routes/admin.routes.js");
const documentRouter = require("./routes/document.routes.js");
const authMiddleware = require("./middlewares/auth.middleware.js");
const requireRole = require("./middlewares/role.middleware.js");

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

console.log("test");

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "api" });
});

app.use("/api/users", userRouter);
app.use("/api/admin", authMiddleware, requireRole("ADMIN"), adminRouter);
app.use("/api/documents", documentRouter);

async function start() {
  try {
    await sequelize.authenticate();
    console.log("Database connected");
    await sequelize.sync({ alter: true });
    console.log("Models synchronized");

    app.listen(PORT, () => {
      console.log(`API running on port ${PORT}`);
    });
  } catch (err) {
    console.error("Failed to start:", err);
    process.exit(1);
  }
}

start();
