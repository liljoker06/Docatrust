const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const DocumentClean = sequelize.define('DocumentClean', {
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
  detected_type: {
    type: DataTypes.ENUM(
      'FACTURE',
      'DEVIS',
      'ATTESTATION_SIRET',
      'VIGILANCE_URSSAF',
      'KBIS',
      'RIB'
    ),
  },
  raw_text_content: {
    type: DataTypes.TEXT,
  },
  extraction_metadata: {
    type: DataTypes.JSONB,
  },
  processed_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'documents_clean',
  timestamps: false,
});

module.exports = DocumentClean;
