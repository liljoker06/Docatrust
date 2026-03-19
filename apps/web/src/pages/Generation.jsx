import "../styles/upload.css";
import "../styles/generation.css";
import { useState } from "react";
import { generation as gen } from "../services/pyraApi";
import { addActivity } from "../lib/activity";

const ITEMS = [
  { key: "devis", label: "Devis", ok: gen.devis, err: gen.devisErronees },
  { key: "factures", label: "Factures", ok: gen.factures, err: gen.facturesErronees },
  { key: "rib", label: "RIB", ok: gen.rib, err: gen.ribErronees },
  { key: "siret", label: "SIRET", ok: gen.siret, err: gen.siretErronees },
  { key: "urssaf", label: "Urssaf", ok: gen.urssaf, err: gen.urssafErronees },
  { key: "kbis", label: "Kbis", ok: gen.kbis, err: gen.kbisErronees },
  { key: "scans", label: "Scans", ok: gen.scans },
  { key: "manifest", label: "Manifest", ok: gen.manifest },
];

export default function Generation() {
  const [loading, setLoading] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const run = async (fn, label, variant = "") => {
    const id = label + variant;
    setLoading(id);
    setError(null);
    setResult(null);
    try {
      const data = await fn();
      setResult({ label: label + (variant ? ` (${variant})` : ""), ...data });
      addActivity({
        type: "generation",
        action: label + (variant ? " erroneous" : " valid"),
        status: "success",
      });
    } catch (e) {
      setError(e.message || "Erreur");
      addActivity({
        type: "generation",
        action: label + (variant ? " erroneous" : " valid"),
        status: "failed",
      });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="upload-page generation-page">
      <div className="upload-header">
        <h1 className="upload-title">Génération (Pyra API)</h1>
        <p className="upload-subtitle">
          Générer des jeux de données : devis, factures, RIB, SIRET, Urssaf, Kbis, scans, manifest.
        </p>
      </div>

      <div className="generation-grid">
        {ITEMS.map(({ key, label, ok, err }) => (
          <div key={key} className="upload-card generation-card">
            <div className="upload-card-head">
              <h3>{label}</h3>
            </div>
            <div className="generation-actions">
              <button
                className="upload-button generation-btn"
                disabled={!!loading}
                onClick={() => run(ok, label)}
              >
                {loading === label ? "Génération…" : "Générer"}
              </button>
              {err && (
                <button
                  className="upload-button generation-btn generation-btn-err"
                  disabled={!!loading}
                  onClick={() => run(err, label, "erronees")}
                >
                  {loading === label + "erronees" ? "Génération…" : "Générer (erreurs)"}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {(result || error) && (
        <div className={`generation-result ${error ? "error" : ""}`}>
          <div className="upload-card-head">
            <h3>{error ? "Erreur" : result?.label}</h3>
          </div>
          {error ? (
            <pre className="generation-output">{error}</pre>
          ) : (
            <pre className="generation-output">
              {result?.output != null ? result.output : JSON.stringify(result?.data ?? result, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
