const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const DocumentRaw = sequelize.define('DocumentRaw', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  uploader_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  minio_object_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  status: {
    type: DataTypes.ENUM('RAW', 'CLEAN', 'CURATED', 'ERROR'),
    defaultValue: 'RAW',
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
  updated_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'documents_raw',
  timestamps: false,
});

module.exports = DocumentRaw;
