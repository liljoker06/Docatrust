import "../styles/upload.css";
import "../styles/generation.css";
import { useEffect, useMemo, useState } from "react";
import { processOcr, getSirene } from "../services/pyraApi";
import { addActivity } from "../lib/activity";
import { addDocument, normalizeDocumentFromOcr } from "../lib/documents";

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function ResultGrid({ data }) {
  if (!data || typeof data !== "object") return null;
  const hiddenKeys = new Set(["ALERTS_JSON", "alerts_json", "ALERTS_CODES", "alerts_codes"]);
  const entries = Object.entries(data).filter(([k]) => !hiddenKeys.has(k));
  if (entries.length === 0) return <p className="ocr-empty">No data returned.</p>;
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

function ResultSummary({ data }) {
  if (!data || typeof data !== "object") return null;
  const alertsCount = Number(data.ALERTS_COUNT ?? data.alerts_count ?? 0) || 0;
  let alerts = data.ALERTS_JSON ?? data.alerts_json ?? [];
  if (typeof alerts === "string") {
    try {
      alerts = JSON.parse(alerts);
    } catch {
      alerts = [];
    }
  }
  if (!Array.isArray(alerts)) alerts = [];

  const hasError = alerts.some((a) => String(a?.level || "").toLowerCase() === "error");
  const status = alertsCount === 0 ? "validated" : hasError ? "rejected" : "warning";
  const statusLabel =
    status === "validated" ? "Validated" : status === "warning" ? "Validated with warnings" : "Rejected";

  return (
    <div className="ocr-summary">
      <div className="ocr-summary-top">
        <span className={`ocr-status-badge ${status}`}>{statusLabel}</span>
        <span className="ocr-alert-count">{alertsCount} alert(s)</span>
      </div>
      {alerts.length > 0 && (
        <ul className="ocr-alert-list">
          {alerts.map((a, idx) => (
            <li key={`${a.code || "alert"}-${idx}`} className="ocr-alert-item">
              <span className={`ocr-alert-level ${String(a.level || "info").toLowerCase()}`}>
                {String(a.level || "info").toUpperCase()}
              </span>
              <div>
                <strong>{a.code || "ALERT"}</strong>
                <p>{a.message || "Alert detected during validation."}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Ocr() {
  const [files, setFiles] = useState([]);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [batchResults, setBatchResults] = useState([]);
  const [ocrError, setOcrError] = useState(null);
  const [ocrProgress, setOcrProgress] = useState(0);

  const [sireneId, setSireneId] = useState("");
  const [sireneLoading, setSireneLoading] = useState(false);
  const [sireneResult, setSireneResult] = useState(null);
  const [sireneError, setSireneError] = useState(null);
  const [sireneProgress, setSireneProgress] = useState(0);

  useEffect(() => {
    if (!ocrLoading) {
      setOcrProgress(0);
      return;
    }
    const timer = setInterval(() => {
      setOcrProgress((prev) => (prev >= 93 ? prev : prev + Math.floor(Math.random() * 9) + 3));
    }, 280);
    return () => clearInterval(timer);
  }, [ocrLoading]);

  useEffect(() => {
    if (!sireneLoading) {
      setSireneProgress(0);
      return;
    }
    const timer = setInterval(() => {
      setSireneProgress((prev) => (prev >= 92 ? prev : prev + Math.floor(Math.random() * 12) + 6));
    }, 220);
    return () => clearInterval(timer);
  }, [sireneLoading]);

  const ocrData = useMemo(() => ocrResult?.data ?? ocrResult, [ocrResult]);
  const sireneData = useMemo(() => sireneResult?.data ?? sireneResult, [sireneResult]);

  const onFileChange = (e) => {
    const selected = Array.from(e.target.files || []);
    setFiles(selected);
    setOcrResult(null);
    setBatchResults([]);
    setOcrError(null);
  };

  const handleProcessOcr = async () => {
    if (files.length === 0) {
      setOcrError("Veuillez sélectionner un ou plusieurs fichiers.");
      return;
    }
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);
    setBatchResults([]);
    try {
      const results = [];
      for (let i = 0; i < files.length; i += 1) {
        const currentFile = files[i];
        try {
          const data = await processOcr(currentFile);
          addDocument(normalizeDocumentFromOcr(data, currentFile.name));
          addActivity({ type: "ocr", action: `process ${currentFile.name}`, status: "success" });
          results.push({
            fileName: currentFile.name,
            status: "success",
            data: data?.data ?? data,
          });
          if (i === 0) {
            setOcrResult(data);
          }
        } catch (e) {
          results.push({
            fileName: currentFile.name,
            status: "failed",
            error: e.message || "OCR processing failed",
          });
          addActivity({ type: "ocr", action: `process ${currentFile.name}`, status: "failed" });
        } finally {
          setOcrProgress(Math.round(((i + 1) / files.length) * 100));
          setBatchResults([...results]);
        }
      }
    } catch (e) {
      setOcrError(e.message || "Erreur lors du traitement OCR.");
    } finally {
      setOcrLoading(false);
    }
  };

  const handleSireneLookup = async () => {
    const id = sireneId.trim();
    if (!id) {
      setSireneError("Saisissez un identifiant SIRET ou SIREN.");
      return;
    }
    setSireneLoading(true);
    setSireneError(null);
    setSireneResult(null);
    try {
      const data = await getSirene(id);
      setSireneProgress(100);
      setSireneResult(data);
      addActivity({ type: "sirene", action: `lookup ${id}`, status: "success" });
    } catch (e) {
      setSireneError(e.message || "Erreur lookup SIRENE.");
      addActivity({ type: "sirene", action: `lookup ${id}`, status: "failed" });
    } finally {
      setSireneLoading(false);
    }
  };

  return (
    <div className="upload-page generation-page">
      <div className="upload-header">
        <h1 className="upload-title">OCR (Pyra API)</h1>
        <p className="upload-subtitle">
          Traiter une facture/image avec OCR ou consulter les données SIRENE par SIRET/SIREN.
        </p>
      </div>

      <div className="upload-grid">
        <div className="upload-card">
          <div className="upload-card-head">
            <h3>Process Invoice (OCR)</h3>
          </div>
          <label className="upload-dropzone">
            <input type="file" accept=".pdf,.png,.jpg,.jpeg" multiple onChange={onFileChange} />
            <div className="upload-dropzone-content">
              <div className="upload-icon">↑</div>
              <h4>Déposer un ou plusieurs fichiers</h4>
              <p>PDF, PNG ou JPG (batch)</p>
            </div>
          </label>
          <label className="upload-dropzone" style={{ marginTop: 10 }}>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              multiple
              webkitdirectory=""
              directory=""
              onChange={onFileChange}
            />
            <div className="upload-dropzone-content">
              <div className="upload-icon">↑</div>
              <h4>Ou sélectionner un dossier complet</h4>
              <p>Tous les fichiers seront traités</p>
            </div>
          </label>
          {files.length > 0 && (
            <div className="selected-file">
              <strong>Fichiers sélectionnés :</strong>
              <span>{files.length} file(s)</span>
              <ul className="batch-files-list">
                {files.slice(0, 8).map((f) => (
                  <li key={`${f.name}-${f.size}`}>{f.webkitRelativePath || f.name}</li>
                ))}
              </ul>
              {files.length > 8 && <span>+ {files.length - 8} more files</span>}
            </div>
          )}
          <button
            className="upload-button"
            disabled={ocrLoading || files.length === 0}
            onClick={handleProcessOcr}
          >
            {ocrLoading ? "Traitement en lot…" : "Traiter avec OCR"}
          </button>
          {ocrLoading && (
            <div className="ocr-progress-wrap">
              <div className="ocr-progress-meta">
                <span>Analyse OCR en cours ({files.length} file(s))...</span>
                <strong>{Math.min(ocrProgress, 100)}%</strong>
              </div>
              <div className="ocr-progress-track">
                <div className="ocr-progress-bar" style={{ width: `${Math.min(ocrProgress, 100)}%` }}></div>
              </div>
            </div>
          )}
          {ocrError && <p className="ocr-error">{ocrError}</p>}
          {ocrResult && (
            <div className="generation-result">
              <div className="upload-card-head"><h3>Résultat OCR (premier fichier)</h3></div>
              <ResultSummary data={ocrData} />
              <ResultGrid data={ocrData} />
            </div>
          )}
          {batchResults.length > 0 && (
            <div className="generation-result">
              <div className="upload-card-head"><h3>Résultats batch</h3></div>
              <div className="batch-result-list">
                {batchResults.map((item) => (
                  <div className="batch-result-item" key={item.fileName}>
                    <strong>{item.fileName}</strong>
                    <span className={`ocr-status-badge ${item.status === "success" ? "validated" : "rejected"}`}>
                      {item.status === "success" ? "Processed" : "Failed"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="upload-card">
          <div className="upload-card-head">
            <h3>Sirene Lookup</h3>
          </div>
          <p className="upload-subtitle" style={{ marginBottom: 12 }}>
            SIRET ou SIREN (9 ou 14 chiffres)
          </p>
          <input
            type="text"
            className="ocr-input"
            placeholder="Ex: 12345678901234"
            value={sireneId}
            onChange={(e) => {
              setSireneId(e.target.value);
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
                <span>Interrogation SIRENE...</span>
                <strong>{Math.min(sireneProgress, 100)}%</strong>
              </div>
              <div className="ocr-progress-track">
                <div
                  className="ocr-progress-bar sirene"
                  style={{ width: `${Math.min(sireneProgress, 100)}%` }}
                ></div>
              </div>
            </div>
          )}
          {sireneError && <p className="ocr-error">{sireneError}</p>}
          {sireneResult && (
            <div className="generation-result">
              <div className="upload-card-head"><h3>Résultat SIRENE</h3></div>
              <ResultGrid data={sireneData} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
