import { useEffect, useState } from "react";
import { api } from "../services/api";

const STATUS_STYLES = {
  SUCCESS: "bg-green-100 text-green-700",
  FAILURE: "bg-red-100 text-red-700",
  SKIPPED: "bg-slate-100 text-slate-500",
};

const STEP_COLORS = {
  RAW: "bg-slate-200",
  CLEAN: "bg-blue-400",
  CURATED: "bg-green-400",
  ERROR: "bg-red-400",
};

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("all");

  useEffect(() => {
    api
      .listLogs()
      .then((d) => setLogs(d.logs))
      .finally(() => setLoading(false));
  }, []);

  const filtered =
    filterStatus === "all"
      ? logs
      : logs.filter((l) => l.status === filterStatus);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2">
        {["all", "SUCCESS", "FAILURE", "SKIPPED"].map((s) => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            className={`text-sm px-3.5 py-1.5 rounded-lg font-medium transition-colors ${
              filterStatus === s
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {s === "all" ? "Tous" : s}
          </button>
        ))}
        <span className="text-xs text-slate-400 ml-1">{filtered.length} entrée{filtered.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-medium text-xs uppercase tracking-wide">
                <th className="text-left px-6 py-3">Fichier</th>
                <th className="text-left px-6 py-3">Transition</th>
                <th className="text-left px-6 py-3">Statut</th>
                <th className="text-left px-6 py-3">DAG run</th>
                <th className="text-left px-6 py-3">Durée</th>
                <th className="text-left px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((log) => {
                const minio = log.DocumentRaw?.minioRaw || log.DocumentRaw?.MinioObject;
                return (
                  <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 text-slate-800 font-medium truncate max-w-[180px]">
                      {minio?.original_filename || log.document_id?.slice(0, 8) + "…" || "—"}
                    </td>

                    {/* from → to */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${STEP_COLORS[log.from_status] || "bg-slate-200"} text-slate-700`}>
                          {log.from_status || "—"}
                        </span>
                        <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                        </svg>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${STEP_COLORS[log.to_status] || "bg-slate-200"} text-slate-700`}>
                          {log.to_status || "—"}
                        </span>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${STATUS_STYLES[log.status] || "bg-slate-100 text-slate-500"}`}>
                        {log.status}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-400 font-mono max-w-[160px] truncate">
                      {log.airflow_run_id || "—"}
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-500">
                      {log.duration_ms ? `${log.duration_ms} ms` : "—"}
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-400">
                      {log.created_at
                        ? new Date(log.created_at).toLocaleString("fr-FR")
                        : "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="text-center py-16 text-slate-400 text-sm">
              Aucun log trouvé.
            </div>
          )}
        </div>
      </div>

      {/* Error details panel */}
      {filtered.some((l) => l.error_message) && (
        <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-5">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Détails des erreurs</h3>
          <div className="space-y-2">
            {filtered
              .filter((l) => l.error_message)
              .map((l) => (
                <div key={l.id} className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2 font-mono break-all">
                  {l.error_message}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
