const sequelize = require('../config/database');

const User = require('./User');
const Token = require('./Token');
const MinioObject = require('./MinioObject');
const DocumentRaw = require('./DocumentRaw');
const DocumentClean = require('./DocumentClean');
const DocumentCurated = require('./DocumentCurated');
const PipelineLog = require('./PipelineLog');
const Inconsistency = require('./Inconsistency');
const CrmEntry = require('./CrmEntry');
const ComplianceAlert = require('./ComplianceAlert');

// ==================== USERS & AUTH ====================

User.hasMany(Token, { foreignKey: 'user_id', onDelete: 'CASCADE' });
Token.belongsTo(User, { foreignKey: 'user_id' });

// ==================== DOCUMENTS RAW ====================

User.hasMany(DocumentRaw, { foreignKey: 'uploader_id' });
DocumentRaw.belongsTo(User, { foreignKey: 'uploader_id', as: 'uploader' });

MinioObject.hasOne(DocumentRaw, { foreignKey: 'minio_object_id' });
DocumentRaw.belongsTo(MinioObject, { foreignKey: 'minio_object_id', as: 'minioRaw' });

// ==================== DOCUMENTS CLEAN ====================

DocumentRaw.hasOne(DocumentClean, { foreignKey: 'document_id' });
DocumentClean.belongsTo(DocumentRaw, { foreignKey: 'document_id' });

MinioObject.hasOne(DocumentClean, { foreignKey: 'minio_object_id' });
DocumentClean.belongsTo(MinioObject, { foreignKey: 'minio_object_id', as: 'minioClean' });

// ==================== DOCUMENTS CURATED ====================

DocumentRaw.hasOne(DocumentCurated, { foreignKey: 'document_id' });
DocumentCurated.belongsTo(DocumentRaw, { foreignKey: 'document_id' });

MinioObject.hasOne(DocumentCurated, { foreignKey: 'minio_object_id' });
DocumentCurated.belongsTo(MinioObject, { foreignKey: 'minio_object_id', as: 'minioCurated' });

// ==================== PIPELINE LOGS ====================

DocumentRaw.hasMany(PipelineLog, { foreignKey: 'document_id' });
PipelineLog.belongsTo(DocumentRaw, { foreignKey: 'document_id' });

// ==================== INCONSISTENCIES ====================

DocumentCurated.hasMany(Inconsistency, { foreignKey: 'curated_id' });
Inconsistency.belongsTo(DocumentCurated, { foreignKey: 'curated_id' });

// ==================== CRM ENTRIES ====================

DocumentCurated.hasMany(CrmEntry, { foreignKey: 'curated_id' });
CrmEntry.belongsTo(DocumentCurated, { foreignKey: 'curated_id' });

// ==================== COMPLIANCE ALERTS ====================

Inconsistency.hasMany(ComplianceAlert, { foreignKey: 'inconsistency_id' });
ComplianceAlert.belongsTo(Inconsistency, { foreignKey: 'inconsistency_id' });

User.hasMany(ComplianceAlert, { foreignKey: 'assigned_to', as: 'assignedAlerts' });
ComplianceAlert.belongsTo(User, { foreignKey: 'assigned_to', as: 'assignee' });

// ==================== EXPORTS ====================

module.exports = {
  sequelize,
  User,
  Token,
  MinioObject,
  DocumentRaw,
  DocumentClean,
  DocumentCurated,
  PipelineLog,
  Inconsistency,
  CrmEntry,
  ComplianceAlert,
};
