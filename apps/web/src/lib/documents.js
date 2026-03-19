const DOCS_KEY = "docatrust_documents";
const LIMIT = 120;

function parseAlerts(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "string") {
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
  return [];
}

export function normalizeDocumentFromOcr(payload, fileName = "Document") {
  const data = payload?.data ?? payload ?? {};
  const alertsCount = Number(data.ALERTS_COUNT ?? data.alerts_count ?? 0) || 0;
  const alerts = parseAlerts(data.ALERTS_JSON ?? data.alerts_json);
  const hasErrorAlert = alerts.some((a) => String(a?.level || "").toLowerCase() === "error");
  const status = alertsCount > 0 ? (hasErrorAlert ? "rejected" : "warning") : "validated";

  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: new Date().toISOString(),
    name: fileName,
    status,
    alertsCount,
    alerts,
    supplierName:
      data.SUPPLIER_NAME ||
      data.FOURNISSEUR_NOM ||
      data.supplier_name ||
      "Unknown supplier",
    invoiceNumber: data.INVOICE_NUMBER || data.NUM_FACTURE || data.invoice_number || "N/A",
    amount: data.TOTAL_TTC || data.MONTANT_TTC || data.total_ttc || null,
    raw: data,
  };
}

export function addDocument(doc) {
  const current = getDocuments();
  const next = [doc, ...current].slice(0, LIMIT);
  localStorage.setItem(DOCS_KEY, JSON.stringify(next));
}

export function getDocuments() {
  try {
    const raw = localStorage.getItem(DOCS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}
