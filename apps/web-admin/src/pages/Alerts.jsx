import { useEffect, useState } from "react";
import { api } from "../services/api";

const SEVERITY_STYLES = {
  HIGH: "bg-red-100 text-red-700 border-red-200",
  MEDIUM: "bg-orange-100 text-orange-700 border-orange-200",
  LOW: "bg-yellow-100 text-yellow-700 border-yellow-200",
};

const TYPE_LABELS = {
  SIRET_MISMATCH: "SIRET non correspondant",
  TVA_INCOHERENTE: "TVA incohérente",
  DATE_EXPIRATION_DEPASSEE: "Date d'expiration dépassée",
  MONTANT_SUSPECT: "Montant suspect",
  DOCUMENT_FALSIFIE: "Document potentiellement falsifié",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // all | open | resolved

  useEffect(() => {
    api
      .listAlerts()
      .then((d) => setAlerts(d.alerts))
      .finally(() => setLoading(false));
  }, []);

  async function handleResolve(id) {
    await api.resolveAlert(id);
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, is_resolved: true, resolved_at: new Date().toISOString() } : a
      )
    );
  }

  const filtered = alerts.filter((a) => {
    if (filter === "open") return !a.is_resolved;
    if (filter === "resolved") return a.is_resolved;
    return true;
  });

  const openCount = alerts.filter((a) => !a.is_resolved).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header filters */}
      <div className="flex items-center gap-3">
        {[
          { key: "all", label: `Toutes (${alerts.length})` },
          { key: "open", label: `Ouvertes (${openCount})` },
          { key: "resolved", label: `Résolues (${alerts.length - openCount})` },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`text-sm px-3.5 py-1.5 rounded-lg font-medium transition-colors ${
              filter === f.key
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Alerts list */}
      <div className="space-y-3">
        {filtered.map((alert) => {
          const inc = alert.Inconsistency || alert.inconsistency;
          const curated = inc?.DocumentCurated || inc?.documentCurated;
          const docRaw = curated?.DocumentRaw || curated?.documentRaw;
          const minio = docRaw?.minioRaw || docRaw?.MinioObject;
          const uploader = docRaw?.uploader;

          return (
            <div
              key={alert.id}
              className={`bg-white rounded-2xl border p-5 shadow-sm ${
                alert.is_resolved ? "opacity-60" : ""
              } ${SEVERITY_STYLES[inc?.severity] || "border-slate-200"}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${SEVERITY_STYLES[inc?.severity] || "bg-slate-100 text-slate-600 border-slate-200"}`}>
                      {inc?.severity || "—"}
                    </span>
                    <span className="text-sm font-semibold text-slate-800">
                      {TYPE_LABELS[inc?.type] || inc?.type || "Anomalie détectée"}
                    </span>
                  </div>

                  {inc?.description && (
                    <p className="text-sm text-slate-600">{inc.description}</p>
                  )}

                  <div className="flex items-center gap-4 text-xs text-slate-400 mt-1">
                    {minio?.original_filename && (
                      <span className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414l-5.414-5.414A1 1 0 0013.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        {minio.original_filename}
                      </span>
                    )}
                    {uploader?.email && (
                      <span>{uploader.email}</span>
                    )}
                    <span>{new Date(alert.created_at).toLocaleDateString("fr-FR")}</span>
                  </div>
                </div>

                <div className="shrink-0">
                  {alert.is_resolved ? (
                    <span className="text-xs font-medium text-green-600 bg-green-50 px-3 py-1.5 rounded-lg">
                      Résolu
                    </span>
                  ) : (
                    <button
                      onClick={() => handleResolve(alert.id)}
                      className="text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg transition-colors"
                    >
                      Marquer résolu
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="text-center py-16 text-slate-400 text-sm">
            Aucune alerte.
          </div>
        )}
      </div>
    </div>
  );
}
