const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Inconsistency = sequelize.define('Inconsistency', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  curated_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  type: {
    type: DataTypes.ENUM(
      'SIRET_MISMATCH',
      'TVA_INCOHERENTE',
      'DATE_EXPIRATION_DEPASSEE',
      'MONTANT_SUSPECT',
      'DOCUMENT_FALSIFIE'
    ),
  },
  severity: {
    type: DataTypes.ENUM('LOW', 'MEDIUM', 'HIGH'),
  },
  description: {
    type: DataTypes.TEXT,
  },
  is_resolved: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  detected_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'inconsistencies',
  timestamps: false,
});

module.exports = Inconsistency;
