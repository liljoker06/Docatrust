const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const CrmEntry = sequelize.define('CrmEntry', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  curated_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  external_crm_ref: {
    type: DataTypes.STRING,
  },
  company_name: {
    type: DataTypes.TEXT,
  },
  sync_status: {
    type: DataTypes.ENUM('PENDING', 'SYNCED', 'FAILED'),
    defaultValue: 'PENDING',
  },
  synced_at: {
    type: DataTypes.DATE,
  },
}, {
  tableName: 'crm_entries',
  timestamps: false,
});

module.exports = CrmEntry;
