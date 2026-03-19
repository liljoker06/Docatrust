import { pyRequest, apiRequest, apiFormRequest, API_BASE } from "./apiClient";
import { getAuthToken } from "../lib/auth";

// ─── OCR & Documents ───────────────────────────────────────────────────────

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  return apiFormRequest("/api/documents/upload", formData);
}

export async function listDocuments() {
  return apiRequest("/api/documents");
}

export async function getDocumentStatus(documentId) {
  return apiRequest(`/api/documents/${documentId}/status`);
}

export async function getDocumentResult(documentId) {
  return apiRequest(`/api/documents/${documentId}/result`);
}

export function getDocumentDownloadUrl(documentId) {
  const token = getAuthToken();
  return `${API_BASE}/api/documents/${documentId}/download?token=${token}`;
}

export async function getSirene(identifier) {
  return pyRequest(`/ocr/sirene/${encodeURIComponent(identifier)}`);
}

async function postGenerate(path) {
  return request(`/generate/${path}`, { method: "POST" });
}

export const generation = {
  devis: () => postGenerate("devis"),
  devisErronees: () => postGenerate("devis-erronees"),
  factures: () => postGenerate("factures"),
  facturesErronees: () => postGenerate("factures-erronees"),
  rib: () => postGenerate("rib"),
  ribErronees: () => postGenerate("rib-erronees"),
  siret: () => postGenerate("siret"),
  siretErronees: () => postGenerate("siret-erronees"),
  urssaf: () => postGenerate("urssaf"),
  urssafErronees: () => postGenerate("urssaf-erronees"),
  kbis: () => postGenerate("kbis"),
  kbisErronees: () => postGenerate("kbis-erronees"),
  scans: () => postGenerate("scans"),
  manifest: () => postGenerate("manifest"),
};
