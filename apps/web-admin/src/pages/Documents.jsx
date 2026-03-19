import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

const STATUS_STYLES = {
  RAW: "bg-slate-100 text-slate-600",
  CLEAN: "bg-blue-100 text-blue-700",
  CURATED: "bg-green-100 text-green-700",
  ERROR: "bg-red-100 text-red-700",
};

function formatBytes(bytes) {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api
      .listAllDocuments()
      .then((d) => setDocuments(d.documents))
      .finally(() => setLoading(false));
  }, []);

  const filtered = documents.filter((doc) => {
    const filename = doc.MinioObject?.original_filename || doc.minioRaw?.original_filename || "";
    const email = doc.uploader?.email || "";
    const q = search.toLowerCase();
    return filename.toLowerCase().includes(q) || email.toLowerCase().includes(q);
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Rechercher par fichier ou utilisateur…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 max-w-sm border border-slate-200 rounded-lg px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-xs text-slate-400">{filtered.length} document{filtered.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-medium text-xs uppercase tracking-wide">
                <th className="text-left px-6 py-3">Fichier</th>
                <th className="text-left px-6 py-3">Déposé par</th>
                <th className="text-left px-6 py-3">Statut</th>
                <th className="text-left px-6 py-3">Taille</th>
                <th className="text-left px-6 py-3">Date</th>
                <th className="text-right px-6 py-3">Détails</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((doc) => {
                const minio = doc.minioRaw || doc.MinioObject;
                return (
                  <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center shrink-0">
                          <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <span className="font-medium text-slate-800 truncate max-w-[200px]">
                          {minio?.original_filename || "—"}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500">{doc.uploader?.email || "—"}</td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${STATUS_STYLES[doc.status] || "bg-slate-100 text-slate-600"}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">{formatBytes(minio?.size_bytes)}</td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {doc.created_at ? new Date(doc.created_at).toLocaleDateString("fr-FR") : "—"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2.5 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                      >
                        Voir
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="text-center py-16 text-slate-400 text-sm">
              Aucun document trouvé.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
