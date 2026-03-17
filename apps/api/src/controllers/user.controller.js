const asyncHandler = require("../utils/asynchandler.util");
const { User, Token } = require("../models/index");
const bcrypt = require("bcrypt");
const { generateToken } = require("../utils/token.util.js");
const { addHours } = require("../utils/date.util.js");

const register = asyncHandler(async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({
      error: true,
      message: "Email and password required.",
    });
  }

  const existingUser = await User.findOne({
    where: { email },
  });

  if (existingUser) {
    return res.status(409).json({
      error: true,
      message: "User already exists.",
    });
  }

  const password_hash = await bcrypt.hash(password, 10);

  const newUser = await User.create({
    email,
    password_hash,
  });

  res.status(201).json({
    error: false,
    user: newUser,
  });
});

const login = asyncHandler(async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res
      .status(400)
      .json({ error: true, message: "Email and password required." });
  }

  const user = await User.findOne({ where: { email } });
  if (!user) {
    return res
      .status(401)
      .json({ error: true, message: "Invalid credentials." });
  }

  const isValid = await bcrypt.compare(password, user.password_hash);
  if (!isValid) {
    return res
      .status(401)
      .json({ error: true, message: "Invalid credentials." });
  }

  await Token.update(
    { is_revoked: true },
    { where: { user_id: user.id, use_case: "API_ACCESS", is_revoked: false } },
  );

  const token_value = generateToken();
  const token_value_hash = await bcrypt.hash(
    token_value,
    parseInt(process.env.BCRYPT_SALT_ROUNDS),
  );

  await Token.create({
    user_id: user.id,
    token_value: token_value_hash,
    use_case: "API_ACCESS",
    expires_at: addHours(
      parseInt(process.env.TOKEN_API_ACCESS_EXPIRES_IN) || 8,
    ),
  });

  return res.status(200).json({
    error: false,
    token: token_value,
    user: { id: user.id, email: user.email, role: user.role },
  });
});

const me = asyncHandler(async (req, res) => {
  const user = req.user;
  return res.status(200).json({ error: false, user: user });
});

module.exports = {
  register,
  login,
  me,
};
