import { useEffect, useState } from "react";
import { api } from "../services/api";

const STATUS_COLORS = {
  RAW: "bg-slate-100 text-slate-600",
  CLEAN: "bg-blue-100 text-blue-700",
  CURATED: "bg-green-100 text-green-700",
  ERROR: "bg-red-100 text-red-700",
};

function StatCard({ label, value, sub, color }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value ?? "—"}</p>
      {sub && <p className="text-xs text-slate-400 mt-2">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getStats()
      .then((d) => setStats(d.stats))
      .catch(() => setError("Impossible de charger les statistiques."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
        {error}
      </div>
    );
  }

  const { totalUsers, totalDocuments, docsByStatus, openAlerts } = stats;

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Utilisateurs" value={totalUsers} color="text-slate-800" />
        <StatCard label="Documents totaux" value={totalDocuments} color="text-blue-700" />
        <StatCard
          label="En attente (CLEAN)"
          value={docsByStatus?.CLEAN}
          sub="Traitement OCR terminé, validation en cours"
          color="text-orange-600"
        />
        <StatCard
          label="Alertes ouvertes"
          value={openAlerts}
          sub="Non résolues"
          color="text-red-600"
        />
      </div>

      {/* Breakdown par statut */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">
          Répartition des documents par statut
        </h2>
        <div className="flex flex-wrap gap-3">
          {Object.entries(docsByStatus || {}).map(([status, count]) => (
            <div
              key={status}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium ${STATUS_COLORS[status] || "bg-slate-100 text-slate-600"}`}
            >
              <span>{status}</span>
              <span className="font-bold">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
