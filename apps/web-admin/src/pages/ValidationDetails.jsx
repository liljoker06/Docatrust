import "../styles/validationDetails.css";

export default function ValidationDetails() {
  return (
    <div className="validation-detail-page">
      <div className="validation-detail-header">
        <h1 className="validation-detail-title">Validation Details</h1>
        <p className="validation-detail-subtitle">
          Review extracted document data and validation status.
        </p>
      </div>

      <div className="validation-detail-panel">
        <div className="validation-detail-panel-head">
          <h3>Document Review</h3>
          <span>•••</span>
        </div>

        <div className="validation-detail-grid">
          <div className="validation-detail-card">
            <span className="validation-detail-label">Document</span>
            <strong className="validation-detail-value">supplier_kbis.pdf</strong>
          </div>

          <div className="validation-detail-card">
            <span className="validation-detail-label">Extracted SIRET</span>
            <strong className="validation-detail-value">123 456 789 00011</strong>
          </div>

          <div className="validation-detail-card">
            <span className="validation-detail-label">Status</span>
            <span className="validation-detail-badge pending">
              Pending manual review
            </span>
          </div>

          <div className="validation-detail-card">
            <span className="validation-detail-label">Reason</span>
            <strong className="validation-detail-value">
              Expiration date needs verification
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}