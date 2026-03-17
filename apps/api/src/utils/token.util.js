const crypto = require("crypto");

const generateToken = () => {
  return crypto.randomBytes(48).toString("hex");
};

module.exports = { generateToken };
