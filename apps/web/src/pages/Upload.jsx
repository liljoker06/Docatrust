import "../styles/upload.css";
import "../styles/generation.css";
import { useEffect, useRef, useMemo, useState } from "react";
import { uploadDocument, getDocumentStatus, getDocumentResult, getSirene } from "../services/pyraApi";
import { addActivity } from "../lib/activity";

// ─── Config ────────────────────────────────────────────────────────────────

const PIPELINE_STATUS_CONFIG = {
  RAW:     { label: "En attente",       className: "warning"   },
  CLEAN:   { label: "OCR terminé",      className: "warning"   },
  CURATED: { label: "Document traité",  className: "validated" },
  ERROR:   { label: "Erreur pipeline",  className: "rejected"  },
};

const UPLOAD_TIPS = [
  "Formats acceptés : PDF, PNG, JPG, TIFF (20 Mo max).",
  "Assurez-vous que le document est lisible et non tronqué.",
  "Types supportés : factures, devis, Kbis, RIB, URSSAF, SIRET.",
  "Le pipeline OCR démarre automatiquement après l'upload.",
  "Vous pouvez uploader plusieurs fichiers en même temps.",
];

// ─── Sous-composants ───────────────────────────────────────────────────────

function PipelineStatusBadge({ status }) {
  const config = PIPELINE_STATUS_CONFIG[status] || { label: status, className: "warning" };
  return <span className={`ocr-status-badge ${config.className}`}>{config.label}</span>;
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function ResultGrid({ data }) {
  if (!data || typeof data !== "object") return null;
  const hiddenKeys = new Set(["alerts_json", "ALERTS_JSON", "alerts_codes", "ALERTS_CODES"]);
  const entries = Object.entries(data).filter(([key]) => !hiddenKeys.has(key));
  if (entries.length === 0) return <p className="ocr-empty">Aucune donnée retournée.</p>;
  return (
    <div className="ocr-result-grid">
      {entries.map(([key, value]) => (
        <div className="ocr-result-item" key={key}>
          <p className="ocr-result-key">{key}</p>
          {typeof value === "object" && value !== null ? (
            <pre className="ocr-result-pre">{formatValue(value)}</pre>
          ) : (
            <p className="ocr-result-value">{formatValue(value)}</p>
          )}
        </div>
      ))}
    </div>
  );
}

function AlertSummary({ data }) {
  if (!data || typeof data !== "object") return null;

  const alertsCount = Number(data.alerts_count ?? data.ALERTS_COUNT ?? 0) || 0;
  let alerts = data.alerts ?? data.alerts_json ?? data.ALERTS_JSON ?? [];
  if (typeof alerts === "string") {
    try { alerts = JSON.parse(alerts); } catch { alerts = []; }
  }
  if (!Array.isArray(alerts)) alerts = [];

  const hasError  = alerts.some((a) => String(a?.level || "").toLowerCase() === "error");
  const badgeType = alertsCount === 0 ? "validated" : hasError ? "rejected" : "warning";
  const badgeLabel =
    badgeType === "validated" ? "Validé" :
    badgeType === "warning"   ? "Validé avec avertissements" : "Rejeté";

  return (
    <div className="ocr-summary">
      <div className="ocr-summary-top">
        <span className={`ocr-status-badge ${badgeType}`}>{badgeLabel}</span>
        <span className="ocr-alert-count">{alertsCount} alerte(s)</span>
      </div>
      {alerts.length > 0 && (
        <ul className="ocr-alert-list">
          {alerts.map((alert, index) => (
            <li key={`${alert.code || "alert"}-${index}`} className="ocr-alert-item">
              <span className={`ocr-alert-level ${String(alert.level || "info").toLowerCase()}`}>
                {String(alert.level || "info").toUpperCase()}
              </span>
              <div>
                <strong>{alert.code || "ALERT"}</strong>
                <p>{alert.message || "Alerte détectée lors de la validation."}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────

export default function Upload() {
  // ── État upload ──
  const [selectedFiles, setSelectedFiles]   = useState([]);
  const [uploadLoading, setUploadLoading]   = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError]       = useState(null);

  // batchResults : [{ fileName, documentId, pipelineStatus, latestLog, alerts, error }]
  const [batchResults, setBatchResults] = useState([]);

  // toast : { message, type: "success"|"error" }
  const [toast, setToast] = useState(null);

  // ── État SIRENE ──
  const [sireneQuery, setSireneQuery]       = useState("");
  const [sireneLoading, setSireneLoading]   = useState(false);
  const [sireneProgress, setSireneProgress] = useState(0);
  const [sireneResult, setSireneResult]     = useState(null);
  const [sireneError, setSireneError]       = useState(null);

  const pollingIntervals = useRef({});

  // ── Progress bars simulées ──
  useEffect(() => {
    if (!uploadLoading) { setUploadProgress(0); return; }
    const timer = setInterval(() => {
      setUploadProgress((prev) => prev >= 90 ? prev : prev + Math.floor(Math.random() * 8) + 3);
    }, 300);
    return () => clearInterval(timer);
  }, [uploadLoading]);

  useEffect(() => {
    if (!sireneLoading) { setSireneProgress(0); return; }
    const timer = setInterval(() => {
      setSireneProgress((prev) => prev >= 90 ? prev : prev + Math.floor(Math.random() * 12) + 6);
    }, 220);
    return () => clearInterval(timer);
  }, [sireneLoading]);

  // Auto-dismiss toast après 4s
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(timer);
  }, [toast]);

  // Nettoyer tous les intervalles au démontage
  useEffect(() => {
    return () => Object.values(pollingIntervals.current).forEach(clearInterval);
  }, []);

  // ── Sélection fichiers ──
  const onFileChange = (event) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
    setBatchResults([]);
    setUploadError(null);
  };

  // ── Upload + déclenchement pipeline ──
  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadError("Veuillez sélectionner un ou plusieurs fichiers.");
      return;
    }
    setUploadLoading(true);
    setUploadError(null);
    setBatchResults([]);

    const results = [];

    for (let index = 0; index < selectedFiles.length; index++) {
      const currentFile = selectedFiles[index];
      try {
        const response = await uploadDocument(currentFile);
        const documentId = response.document_id;

        results.push({
          fileName:       currentFile.name,
          documentId,
          pipelineStatus: "RAW",
          latestLog:      null,
          error:          null,
        });
        setBatchResults([...results]);
        addActivity({ type: "upload", action: currentFile.name, status: "success" });
        setToast({ message: `"${currentFile.name}" uploadé — pipeline OCR en cours…`, type: "success" });

        startPolling(documentId, results, results.length - 1, setBatchResults);
      } catch (uploadError) {
        results.push({
          fileName:       currentFile.name,
          documentId:     null,
          pipelineStatus: "ERROR",
          latestLog:      null,
          error:          uploadError.message || "Échec de l'upload.",
        });
        setBatchResults([...results]);
        addActivity({ type: "upload", action: currentFile.name, status: "failed" });
      }

      setUploadProgress(Math.round(((index + 1) / selectedFiles.length) * 100));
    }

    setUploadLoading(false);
  };

  // ── Polling statut pipeline ──
  function startPolling(documentId, resultsRef, resultIndex, setResults) {
    const FINAL_STATUSES      = ["CURATED", "ERROR"];
    const POLLING_INTERVAL_MS = 3000;

    const intervalId = setInterval(async () => {
      try {
        const statusResponse = await getDocumentStatus(documentId);
        resultsRef[resultIndex] = {
          ...resultsRef[resultIndex],
          pipelineStatus: statusResponse.status,
          latestLog:      statusResponse.latest_log,
        };
        setResults([...resultsRef]);

        if (FINAL_STATUSES.includes(statusResponse.status)) {
          clearInterval(pollingIntervals.current[documentId]);
          delete pollingIntervals.current[documentId];

          if (statusResponse.status === "CURATED") {
            try {
              const resultResponse = await getDocumentResult(documentId);
              const resultData = resultResponse.result ?? resultResponse;
              let alerts = resultData.alerts ?? resultData.alerts_json ?? resultData.ALERTS_JSON ?? [];
              if (typeof alerts === "string") {
                try { alerts = JSON.parse(alerts); } catch { alerts = []; }
              }
              if (!Array.isArray(alerts)) alerts = [];
              resultsRef[resultIndex] = {
                ...resultsRef[resultIndex],
                alerts,
                resultData,
              };
              setResults([...resultsRef]);
              setToast({
                message: `"${resultsRef[resultIndex].fileName}" traité — ${alerts.length} alerte(s)`,
                type: alerts.some((a) => String(a?.level || "").toLowerCase() === "error") ? "error" : "success",
              });
            } catch {
              // résultat pas encore dispo, pas bloquant
            }
          }
        }
      } catch {
        // On continue le polling même si une requête échoue temporairement
      }
    }, POLLING_INTERVAL_MS);

    pollingIntervals.current[documentId] = intervalId;
  }

  // ── Lookup SIRENE ──
  const handleSireneLookup = async () => {
    const cleanedId = sireneQuery.trim();
    if (!cleanedId) {
      setSireneError("Saisissez un identifiant SIRET ou SIREN.");
      return;
    }
    setSireneLoading(true);
    setSireneError(null);
    setSireneResult(null);
    try {
      const data = await getSirene(cleanedId);
      setSireneProgress(100);
      setSireneResult(data);
      addActivity({ type: "sirene", action: `lookup ${cleanedId}`, status: "success" });
    } catch (lookupError) {
      setSireneError(lookupError.message || "Erreur lors de la recherche SIRENE.");
      addActivity({ type: "sirene", action: `lookup ${cleanedId}`, status: "failed" });
    } finally {
      setSireneLoading(false);
    }
  };

  const sireneData = useMemo(() => sireneResult?.data ?? sireneResult, [sireneResult]);

  // ─── Rendu ───────────────────────────────────────────────────────────────

  return (
    <div className="upload-page generation-page">
      <div className="upload-header">
        <h1 className="upload-title">Upload de documents</h1>
        <p className="upload-subtitle">
          Déposez vos documents pour lancer le pipeline OCR, ou vérifiez une entreprise via SIRET/SIREN.
        </p>
      </div>

      <div className="upload-grid">

        {/* ── Panel Upload ── */}
        <div className="upload-card">
          <div className="upload-card-head">
            <h3>Déposer des documents</h3>
          </div>

          <label className="upload-dropzone">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              multiple
              onChange={onFileChange}
            />
            <div className="upload-dropzone-content">
              <div className="upload-icon">↑</div>
              <h4>Glisser-déposer ou cliquer pour parcourir</h4>
              <p>PDF, PNG, JPG, TIFF — 20 Mo max par fichier</p>
            </div>
          </label>

          <label className="upload-dropzone" style={{ marginTop: 10 }}>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              multiple
              webkitdirectory=""
              directory=""
              onChange={onFileChange}
            />
            <div className="upload-dropzone-content">
              <div className="upload-icon">↑</div>
              <h4>Ou sélectionner un dossier complet</h4>
              <p>Tous les fichiers seront traités en batch</p>
            </div>
          </label>

          {selectedFiles.length > 0 && (
            <div className="selected-file">
              <strong>{selectedFiles.length} fichier(s) sélectionné(s)</strong>
              <ul className="batch-files-list">
                {selectedFiles.slice(0, 8).map((file) => (
                  <li key={`${file.name}-${file.size}`}>
                    {file.webkitRelativePath || file.name}
                  </li>
                ))}
              </ul>
              {selectedFiles.length > 8 && (
                <span>+ {selectedFiles.length - 8} fichiers supplémentaires</span>
              )}
            </div>
          )}

          <button
            className="upload-button"
            disabled={uploadLoading || selectedFiles.length === 0}
            onClick={handleUpload}
          >
            {uploadLoading ? "Upload en cours…" : "Lancer le pipeline OCR"}
          </button>

          {uploadLoading && (
            <div className="ocr-progress-wrap">
              <div className="ocr-progress-meta">
                <span>Envoi des fichiers ({selectedFiles.length})…</span>
                <strong>{Math.min(uploadProgress, 100)}%</strong>
              </div>
              <div className="ocr-progress-track">
                <div
                  className="ocr-progress-bar"
                  style={{ width: `${Math.min(uploadProgress, 100)}%` }}
                />
              </div>
            </div>
          )}

          {uploadError && <p className="ocr-error">{uploadError}</p>}

          {/* Suivi pipeline batch */}
          {batchResults.length > 0 && (
            <div className="generation-result">
              <div className="upload-card-head">
                <h3>Suivi du pipeline</h3>
              </div>
              <div className="batch-result-list">
                {batchResults.map((result) => (
                  <div className="batch-result-item" key={result.fileName} style={{ flexDirection: "column", alignItems: "stretch", gap: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <strong>{result.fileName}</strong>
                        {result.documentId && (
                          <p style={{ fontSize: "0.75rem", opacity: 0.55, marginTop: 2 }}>
                            {result.documentId}
                          </p>
                        )}
                        {result.error && (
                          <p className="ocr-error" style={{ marginTop: 4 }}>{result.error}</p>
                        )}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                        <PipelineStatusBadge status={result.pipelineStatus} />
                        {result.pipelineStatus !== "CURATED" && result.pipelineStatus !== "ERROR" && result.documentId && (
                          <span style={{ fontSize: "0.7rem", opacity: 0.5 }}>Actualisation…</span>
                        )}
                      </div>
                    </div>
                    {result.pipelineStatus === "CURATED" && result.alerts !== undefined && (
                      <AlertSummary data={{ ...result.resultData, alerts: result.alerts }} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Conseils */}
          <div className="upload-side-card" style={{ marginTop: 16 }}>
            <div className="upload-card-head">
              <h3>Conseils</h3>
            </div>
            <ul className="upload-tips">
              {UPLOAD_TIPS.map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* ── Panel SIRENE ── */}
        <div className="upload-card">
          <div className="upload-card-head">
            <h3>Recherche SIRENE</h3>
          </div>
          <p className="upload-subtitle" style={{ marginBottom: 12 }}>
            Vérifiez une entreprise via son SIRET (14 chiffres) ou SIREN (9 chiffres).
          </p>

          <input
            type="text"
            className="ocr-input"
            placeholder="Ex : 12345678901234"
            value={sireneQuery}
            onChange={(e) => {
              setSireneQuery(e.target.value);
              setSireneResult(null);
              setSireneError(null);
            }}
          />

          <button
            className="upload-button"
            disabled={sireneLoading}
            onClick={handleSireneLookup}
          >
            {sireneLoading ? "Recherche…" : "Rechercher"}
          </button>

          {sireneLoading && (
            <div className="ocr-progress-wrap">
              <div className="ocr-progress-meta">
                <span>Interrogation de la base INSEE…</span>
                <strong>{Math.min(sireneProgress, 100)}%</strong>
              </div>
              <div className="ocr-progress-track">
                <div
                  className="ocr-progress-bar sirene"
                  style={{ width: `${Math.min(sireneProgress, 100)}%` }}
                />
              </div>
            </div>
          )}

          {sireneError && <p className="ocr-error">{sireneError}</p>}

          {sireneResult && (
            <div className="generation-result">
              <div className="upload-card-head"><h3>Résultat SIRENE</h3></div>
              <AlertSummary data={sireneData} />
              <ResultGrid data={sireneData} />
            </div>
          )}
        </div>

      </div>

      {/* Toast notification */}
      {toast && (
        <div className={`upload-toast ${toast.type}`}>
          {toast.message}
        </div>
      )}
    </div>
  );
}
