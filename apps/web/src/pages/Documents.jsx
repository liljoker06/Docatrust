import "../styles/documents.css";
import "../styles/generation.css";
import "../styles/upload.css";
import { useEffect, useState } from "react";
import { listDocuments, getDocumentResult, getDocumentDownloadUrl } from "../services/pyraApi";

const STATUS_LABEL = {
  RAW:     { label: "En attente",      cls: "warning"   },
  CLEAN:   { label: "OCR terminé",     cls: "warning"   },
  CURATED: { label: "Traité",          cls: "validated" },
  ERROR:   { label: "Erreur",          cls: "rejected"  },
};

function StatusBadge({ status }) {
  const cfg = STATUS_LABEL[status] || { label: status, cls: "pending" };
  return <span className={`doc-badge ${cfg.cls}`}>{cfg.label}</span>;
}

function AlertList({ alerts }) {
  if (!alerts || alerts.length === 0) return null;
  return (
    <ul className="document-alerts">
      {alerts.slice(0, 5).map((a, i) => (
        <li key={`${a.code || "a"}-${i}`} className="ocr-alert-item">
          <span className={`ocr-alert-level ${String(a.level || "info").toLowerCase()}`}>
            {String(a.level || "info").toUpperCase()}
          </span>
          <div>
            <strong>{a.code || "ALERT"}</strong>
            <p>{a.message || "Alerte détectée."}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}

function DocumentCard({ doc }) {
  const [expanded, setExpanded]   = useState(false);
  const [resultData, setResult]   = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  const filename = doc.minioRaw?.original_filename || doc.id;
  const status   = doc.status;

  async function loadResult() {
    if (resultData) { setExpanded((v) => !v); return; }
    setLoading(true);
    setError(null);
    try {
      const res  = await getDocumentResult(doc.id);
      const data = res.result ?? res;
      let alerts = data.alerts ?? data.alerts_json ?? data.ALERTS_JSON ?? [];
      if (typeof alerts === "string") { try { alerts = JSON.parse(alerts); } catch { alerts = []; } }
      if (!Array.isArray(alerts)) alerts = [];
      setResult({ ...data, _alerts: alerts });
      setExpanded(true);
    } catch (e) {
      setError(e.message || "Résultat indisponible.");
    } finally {
      setLoading(false);
    }
  }

  const alertsCount = resultData?._alerts?.length ?? 0;
  const hasError    = resultData?._alerts?.some((a) => String(a?.level || "").toLowerCase() === "error");
  const badgeCls    = !resultData ? "" : alertsCount === 0 ? "validated" : hasError ? "rejected" : "warning";
  const badgeLabel  = !resultData ? null : alertsCount === 0 ? "Validé" : hasError ? "Rejeté" : "Avertissements";

  return (
    <article className="document-card">
      <div className="document-head">
        <h3 className="document-title">{filename}</h3>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {badgeLabel && <span className={`doc-badge ${badgeCls}`}>{badgeLabel}</span>}
          <StatusBadge status={status} />
        </div>
      </div>

      <p className="document-meta">
        <strong>Date :</strong> {new Date(doc.created_at || doc.createdAt).toLocaleString("fr-FR")}
      </p>
      <p className="document-meta">
        <strong>ID :</strong> <span style={{ opacity: 0.55, fontSize: "0.75rem" }}>{doc.id}</span>
      </p>

      <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
        {status === "CURATED" && (
          <button className="upload-button" style={{ flex: 1, padding: "7px 12px", fontSize: 13 }} onClick={loadResult} disabled={loading}>
            {loading ? "Chargement…" : expanded ? "Masquer le résumé" : "Voir le résumé"}
          </button>
        )}
        <a
          href={getDocumentDownloadUrl(doc.id)}
          className="upload-button"
          style={{ flex: 1, padding: "7px 12px", fontSize: 13, textAlign: "center", textDecoration: "none" }}
          download
        >
          Télécharger
        </a>
      </div>

      {error && <p className="ocr-error" style={{ marginTop: 8 }}>{error}</p>}

      {expanded && resultData && (
        <div style={{ marginTop: 12 }}>
          <AlertList alerts={resultData._alerts} />
          {alertsCount === 0 && (
            <p style={{ fontSize: 13, opacity: 0.7, marginTop: 6 }}>Aucune alerte — document validé.</p>
          )}
        </div>
      )}
    </article>
  );
}

export default function Documents() {
  const [docs, setDocs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await listDocuments();
        setDocs(res.documents ?? []);
      } catch (e) {
        setError(e.message || "Impossible de charger les documents.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="documents-page">
      <div className="upload-header">
        <h1 className="upload-title">Documents</h1>
        <p className="upload-subtitle">Historique des documents uploadés et résultats du pipeline OCR.</p>
      </div>

      {loading && <p style={{ color: "#fff", opacity: 0.7 }}>Chargement…</p>}
      {error   && <p className="ocr-error">{error}</p>}

      {!loading && !error && docs.length === 0 && (
        <div className="document-empty">
          Aucun document. Uploadez un fichier depuis la page Upload.
        </div>
      )}

      <div className="documents-grid">
        {docs.map((doc) => (
          <DocumentCard key={doc.id} doc={doc} />
        ))}
      </div>
    </div>
  );
}
