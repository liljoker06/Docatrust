import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../services/api";

const STATUS_STYLES = {
  RAW: "bg-slate-100 text-slate-600",
  CLEAN: "bg-blue-100 text-blue-700",
  CURATED: "bg-green-100 text-green-700",
  ERROR: "bg-red-100 text-red-700",
};

const SEVERITY_STYLES = {
  HIGH: "bg-red-100 text-red-700",
  MEDIUM: "bg-orange-100 text-orange-700",
  LOW: "bg-yellow-100 text-yellow-700",
};

const TYPE_LABELS = {
  SIRET_MISMATCH: "SIRET non correspondant",
  TVA_INCOHERENTE: "TVA incohérente",
  DATE_EXPIRATION_DEPASSEE: "Date d'expiration dépassée",
  MONTANT_SUSPECT: "Montant suspect",
  DOCUMENT_FALSIFIE: "Document potentiellement falsifié",
};

const LOG_STATUS_STYLES = {
  SUCCESS: "bg-green-400",
  FAILURE: "bg-red-400",
  SKIPPED: "bg-slate-300",
};

function Section({ title, children }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
      <h2 className="text-sm font-semibold text-slate-700 mb-4">{title}</h2>
      {children}
    </div>
  );
}

export default function ValidationDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getDocumentDetails(id)
      .then((d) => setDoc(d.document))
      .catch(() => setError("Document introuvable."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate("/documents")} className="text-sm text-blue-600 hover:underline flex items-center gap-1">
          ← Retour aux documents
        </button>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error || "Document introuvable."}
        </div>
      </div>
    );
  }

  const minio = doc.minioRaw || doc.MinioObject;
  const clean = doc.DocumentClean;
  const curated = doc.DocumentCurated;
  const inconsistencies = curated?.Inconsistencies || curated?.inconsistencies || [];
  const logs = doc.PipelineLogs || doc.pipelineLogs || [];

  return (
    <div className="space-y-5">
      <button onClick={() => navigate("/documents")} className="text-sm text-blue-600 hover:underline flex items-center gap-1">
        ← Retour aux documents
      </button>

      {/* Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-lg font-bold text-slate-900">{minio?.original_filename || "Document sans nom"}</h1>
          <p className="text-sm text-slate-500">
            Déposé par <span className="font-medium">{doc.uploader?.email || "—"}</span>
            {doc.created_at && <> · {new Date(doc.created_at).toLocaleString("fr-FR")}</>}
          </p>
        </div>
        <span className={`text-xs font-bold px-3 py-1.5 rounded-full shrink-0 ${STATUS_STYLES[doc.status] || "bg-slate-100 text-slate-600"}`}>
          {doc.status}
        </span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        {/* OCR data */}
        <Section title="Résultat OCR">
          {clean ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Type détecté</span>
                <span className="text-xs font-semibold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg">{clean.detected_type || "—"}</span>
              </div>
              {clean.extraction_metadata && (
                <div>
                  <p className="text-xs text-slate-500 mb-1.5">Champs extraits</p>
                  <pre className="text-xs bg-slate-50 rounded-xl p-4 overflow-auto max-h-60 text-slate-700 font-mono">
                    {JSON.stringify(clean.extraction_metadata, null, 2)}
                  </pre>
                </div>
              )}
              {clean.raw_text_content && (
                <div>
                  <p className="text-xs text-slate-500 mb-1.5">Texte brut</p>
                  <div className="text-xs bg-slate-50 rounded-xl p-4 max-h-40 overflow-auto text-slate-600 whitespace-pre-wrap font-mono">
                    {clean.raw_text_content}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-400">Traitement OCR pas encore effectué.</p>
          )}
        </Section>

        {/* Inconsistencies */}
        <Section title={`Inconsistances (${inconsistencies.length})`}>
          {inconsistencies.length === 0 ? (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Aucune anomalie détectée
            </div>
          ) : (
            <div className="space-y-2.5">
              {inconsistencies.map((inc) => (
                <div key={inc.id} className={`rounded-xl px-4 py-3 ${SEVERITY_STYLES[inc.severity] || "bg-slate-100 text-slate-600"}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold">{inc.severity}</span>
                    <span className="text-xs font-semibold">{TYPE_LABELS[inc.type] || inc.type}</span>
                  </div>
                  {inc.description && <p className="text-xs opacity-80">{inc.description}</p>}
                  <p className="text-xs opacity-60 mt-1">
                    {inc.is_resolved ? "Résolu" : "Non résolu"} · {new Date(inc.detected_at).toLocaleDateString("fr-FR")}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Section>
      </div>

      {/* Pipeline timeline */}
      <Section title="Timeline du pipeline">
        {logs.length === 0 ? (
          <p className="text-sm text-slate-400">Aucun log de pipeline.</p>
        ) : (
          <div className="relative pl-5">
            <div className="absolute left-1.5 top-0 bottom-0 w-px bg-slate-200" />
            <div className="space-y-4">
              {logs.map((log) => (
                <div key={log.id} className="relative flex gap-4 items-start">
                  <div className={`absolute -left-4 w-3 h-3 rounded-full border-2 border-white mt-0.5 ${LOG_STATUS_STYLES[log.status] || "bg-slate-300"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium text-slate-800">{log.from_status} → {log.to_status}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${log.status === "SUCCESS" ? "bg-green-100 text-green-700" : log.status === "FAILURE" ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-500"}`}>
                        {log.status}
                      </span>
                      {log.duration_ms && <span className="text-xs text-slate-400">{log.duration_ms} ms</span>}
                    </div>
                    {log.error_message && (
                      <p className="text-xs text-red-600 mt-1 font-mono bg-red-50 rounded px-2 py-1">{log.error_message}</p>
                    )}
                    <p className="text-xs text-slate-400 mt-0.5">{new Date(log.created_at).toLocaleString("fr-FR")}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Section>
    </div>
  );
}
