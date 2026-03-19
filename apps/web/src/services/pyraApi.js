import { pyRequest, PY_BASE } from "./apiClient";

async function request(path, options = {}) {
  return pyRequest(path, {
    ...options,
    headers: { ...options.headers },
  });
}

export async function processOcr(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${PY_BASE}/ocr/process`, {
    method: "POST",
    body: form,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.message || res.statusText);
  return data;
}

export async function getSirene(identifier) {
  return request(`/ocr/sirene/${encodeURIComponent(identifier)}`);
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
