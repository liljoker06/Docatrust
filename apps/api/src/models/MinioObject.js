const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const MinioObject = sequelize.define('MinioObject', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  bucket_name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  zone: {
    type: DataTypes.ENUM('RAW', 'CLEAN', 'CURATED'),
    allowNull: false,
  },
  object_key: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  original_filename: {
    type: DataTypes.STRING,
  },
  mime_type: {
    type: DataTypes.STRING,
  },
  size_bytes: {
    type: DataTypes.BIGINT,
  },
  checksum_sha256: {
    type: DataTypes.STRING,
  },
  is_encrypted: {
    type: DataTypes.BOOLEAN,
    defaultValue: true,
  },
  uploaded_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'minio_objects',
  timestamps: false,
  indexes: [
    {
      unique: true,
      fields: ['bucket_name', 'object_key'],
    },
  ],
});

module.exports = MinioObject;
