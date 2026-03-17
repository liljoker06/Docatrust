const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PipelineLog = sequelize.define('PipelineLog', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  document_id: {
    type: DataTypes.UUID,
    allowNull: false,
  },
  from_status: {
    type: DataTypes.ENUM('RAW', 'CLEAN', 'CURATED', 'ERROR'),
  },
  to_status: {
    type: DataTypes.ENUM('RAW', 'CLEAN', 'CURATED', 'ERROR'),
  },
  status: {
    type: DataTypes.ENUM('SUCCESS', 'FAILURE', 'SKIPPED'),
  },
  airflow_dag_id: {
    type: DataTypes.STRING,
  },
  airflow_run_id: {
    type: DataTypes.STRING,
  },
  error_message: {
    type: DataTypes.TEXT,
  },
  duration_ms: {
    type: DataTypes.INTEGER,
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'pipeline_logs',
  timestamps: false,
});

module.exports = PipelineLog;
