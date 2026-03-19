require("dotenv").config({ path: require("path").resolve(__dirname, "../../.env") });
const bcrypt = require("bcrypt");
const { sequelize, User } = require("../models/index");

const ADMIN_EMAIL = process.env.SEED_ADMIN_EMAIL || "admin@gmail.com";
const ADMIN_PASSWORD = process.env.SEED_ADMIN_PASSWORD || "admin";

async function seed() {
  try {
    await sequelize.authenticate();
    await sequelize.sync({ alter: true });

    const existing = await User.findOne({ where: { email: ADMIN_EMAIL } });

    if (existing) {
      // S'assure que le rôle est bien ADMIN
      await existing.update({ role: "ADMIN", is_active: true });
      console.log(`[seed] Compte mis à jour en ADMIN : ${ADMIN_EMAIL}`);
    } else {
      const password_hash = await bcrypt.hash(ADMIN_PASSWORD, 10);
      await User.create({ email: ADMIN_EMAIL, password_hash, role: "ADMIN" });
      console.log(`[seed] Compte admin créé : ${ADMIN_EMAIL}`);
    }

    console.log("[seed] Terminé.");
    process.exit(0);
  } catch (err) {
    console.error("[seed] Erreur :", err.message);
    process.exit(1);
  }
}

seed();
