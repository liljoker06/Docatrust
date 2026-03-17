const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const ComplianceAlert = sequelize.define('ComplianceAlert', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  inconsistency_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  assigned_to: {
    type: DataTypes.UUID,
  },
  is_resolved: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  resolved_at: {
    type: DataTypes.DATE,
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'compliance_alerts',
  timestamps: false,
});

module.exports = ComplianceAlert;
