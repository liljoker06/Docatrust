import "../styles/documents.css";
import { useMemo } from "react";
import { getDocuments } from "../lib/documents";

function statusLabel(status) {
  if (status === "validated") return "Validated";
  if (status === "warning") return "Warning";
  if (status === "rejected") return "Rejected";
  return "Unknown";
}

export default function Documents() {
  const docs = useMemo(() => getDocuments(), []);

  return (
    <div className="documents-page">
      <div className="upload-header">
        <h1 className="upload-title">Documents</h1>
        <p className="upload-subtitle">All processed documents with validation status and alerts.</p>
      </div>

      {docs.length === 0 && (
        <div className="document-empty">
          No documents yet. Process a file from `OCR` or `Upload` page and it will appear here.
        </div>
      )}

      <div className="documents-grid">
        {docs.map((doc) => (
          <article className="document-card" key={doc.id}>
            <div className="document-head">
              <h3 className="document-title">{doc.name}</h3>
              <span className={`badge ${doc.status}`}>{statusLabel(doc.status)}</span>
            </div>

            <p className="document-meta">
              <strong>Date:</strong> {new Date(doc.createdAt).toLocaleString()}
            </p>
            <p className="document-meta">
              <strong>Supplier:</strong> {doc.supplierName || "Unknown"}
            </p>
            <p className="document-meta">
              <strong>Invoice #:</strong> {doc.invoiceNumber || "N/A"}
            </p>
            <p className="document-meta">
              <strong>Alerts:</strong> {doc.alertsCount || 0}
            </p>

            {Array.isArray(doc.alerts) && doc.alerts.length > 0 && (
              <div className="document-alerts">
                <strong style={{ color: "#fff", fontSize: 13 }}>Main alerts</strong>
                <ul>
                  {doc.alerts.slice(0, 3).map((a, idx) => (
                    <li key={`${a.code || "a"}-${idx}`}>
                      <strong>{a.code || "ALERT"}:</strong> {a.message || "Validation alert"}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}