const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const DocumentCurated = sequelize.define('DocumentCurated', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  document_id: {
    type: DataTypes.UUID,
    allowNull: false,
    unique: true,
  },
  minio_object_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  siret_encrypted: {
    type: DataTypes.TEXT,
  },
  company_name_encrypted: {
    type: DataTypes.TEXT,
  },
  amount_ht_encrypted: {
    type: DataTypes.TEXT,
  },
  amount_ttc_encrypted: {
    type: DataTypes.TEXT,
  },
  vat_amount_encrypted: {
    type: DataTypes.TEXT,
  },
  rib_encrypted: {
    type: DataTypes.TEXT,
  },
  emission_date: {
    type: DataTypes.DATEONLY,
  },
  expiry_date: {
    type: DataTypes.DATEONLY,
  },
  is_valid: {
    type: DataTypes.BOOLEAN,
    defaultValue: true,
  },
  last_update: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'documents_curated',
  timestamps: false,
});

module.exports = DocumentCurated;
