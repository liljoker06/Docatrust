const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Token = sequelize.define('Token', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  user_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  token_value: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  use_case: {
    type: DataTypes.ENUM(
      'EMAIL_VERIFICATION',
      'PASSWORD_RESET',
      'DOCUMENT_EXTERNAL_VALIDATION',
      'API_ACCESS'
    ),
  },
  is_revoked: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  expires_at: {
    type: DataTypes.DATE,
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'tokens',
  timestamps: false,
});

module.exports = Token;
