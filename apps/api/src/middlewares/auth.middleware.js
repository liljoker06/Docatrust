const bcrypt = require("bcrypt");
const { Token, User } = require("../models");
const asyncHandler = require("../utils/asynchandler.util.js");
const { isExpired } = require("../utils/date.util.js");

const authMiddleware = asyncHandler(async (req, res, next) => {
  const header = req.headers.authorization;
  let token_value = null;

  if (header && header.startsWith("Bearer ")) {
    token_value = header.split(" ")[1];
  } else if (req.query.token) {
    token_value = req.query.token;
  }

  if (!token_value) {
    return res.status(401).json({ error: true, message: "Missing token" });
  }

  const tokens = await Token.findAll({
    where: { use_case: "API_ACCESS", is_revoked: false },
  });

  let matchedToken = null;
  for (const token of tokens) {
    const isMatch = await bcrypt.compare(token_value, token.token_value);
    if (isMatch) {
      matchedToken = token;
      break;
    }
  }

  if (!matchedToken) {
    return res.status(401).json({ error: true, message: "Invalid token" });
  }

  if (isExpired(matchedToken.expires_at)) {
    return res.status(401).json({ error: true, message: "Token expired" });
  }

  req.user = await User.findByPk(matchedToken.user_id);

  next();
});

module.exports = authMiddleware;
