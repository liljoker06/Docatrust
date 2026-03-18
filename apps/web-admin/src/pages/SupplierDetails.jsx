import { useParams } from "react-router-dom";
import "../styles/supplierDetail.css";

export default function SupplierDetails() {
  const { id } = useParams();

  return (
    <div className="supplier-detail-page">
      <div className="supplier-detail-header">
        <h1 className="supplier-detail-title">Supplier Details</h1>
        <p className="supplier-detail-subtitle">
          Detailed information about supplier #{id}
        </p>
      </div>

      <div className="supplier-detail-panel">
        <div className="supplier-detail-panel-head">
          <h3>Information</h3>
          <span>•••</span>
        </div>

        <div className="supplier-detail-grid">
          <div className="supplier-detail-card">
            <span className="supplier-detail-label">Supplier ID</span>
            <strong className="supplier-detail-value">{id}</strong>
          </div>

          <div className="supplier-detail-card">
            <span className="supplier-detail-label">Name</span>
            <strong className="supplier-detail-value">Supplier {id}</strong>
          </div>

          <div className="supplier-detail-card">
            <span className="supplier-detail-label">Status</span>
            <span className="supplier-detail-badge pending">Pending</span>
          </div>

          <div className="supplier-detail-card">
            <span className="supplier-detail-label">Last document</span>
            <strong className="supplier-detail-value">KBIS.pdf</strong>
          </div>
        </div>
      </div>
    </div>
  );
}