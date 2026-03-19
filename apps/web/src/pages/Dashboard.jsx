import "../styles/dashboard.css";
import { useEffect, useMemo, useState } from "react";
import { getAuthSession } from "../lib/auth";
import { meApi } from "../services/authApi";
import { API_BASE, PY_BASE } from "../services/apiClient";
import { listDocuments, getDocumentResult } from "../services/pyraApi";

function parseAlerts(result) {
  if (!result) return [];
  let alerts = result.alerts ?? result.alerts_json ?? result.ALERTS_JSON ?? [];
  if (typeof alerts === "string") {
    try {
      alerts = JSON.parse(alerts);
    } catch {
      alerts = [];
    }
  }
  return Array.isArray(alerts) ? alerts : [];
}

function classifyDocument(doc, result) {
  const status = String(doc?.status || "").toUpperCase();
  if (status === "ERROR") return "rejected";
  if (status === "RAW") return "warning";
  if (!result) return status === "CURATED" ? "validated" : "warning";

  const alerts = parseAlerts(result);
  if (alerts.length === 0) return "validated";
  const hasError = alerts.some((a) => String(a?.level || "").toLowerCase() === "error");
  return hasError ? "rejected" : "warning";
}

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [apiHealth, setApiHealth] = useState("loading");
  const [pyHealth, setPyHealth] = useState("loading");
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const me = await meApi();
        if (alive) setUser(me.user);
      } catch {
        if (alive) setUser(getAuthSession());
      }
    })();

    (async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!alive) return;
        setApiHealth(res.ok ? "up" : "down");
      } catch {
        if (alive) setApiHealth("down");
      }
    })();

    (async () => {
      try {
        const res = await fetch(`${PY_BASE}/health`);
        if (!alive) return;
        setPyHealth(res.ok ? "up" : "down");
      } catch {
        if (alive) setPyHealth("down");
      }
    })();

    (async () => {
      try {
        const res = await listDocuments();
        if (!alive) return;
        const docs = res.documents ?? [];

        const enriched = await Promise.all(
          docs.map(async (doc) => {
            const base = {
              id: doc.id,
              name: doc.minioRaw?.original_filename || doc.id,
              createdAt: doc.created_at || doc.createdAt || new Date().toISOString(),
              apiStatus: doc.status,
            };

            if (!["CLEAN", "CURATED", "ERROR"].includes(String(doc.status || "").toUpperCase())) {
              return { ...base, status: classifyDocument(doc, null) };
            }

            try {
              const detail = await getDocumentResult(doc.id);
              return { ...base, status: classifyDocument(doc, detail?.result), result: detail?.result };
            } catch {
              return { ...base, status: classifyDocument(doc, null) };
            }
          })
        );

        if (alive) setDocuments(enriched);
      } catch (e) {
        if (alive) setDashboardError(e.message || "Unable to load dashboard data.");
      } finally {
        if (alive) setDashboardLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  const computed = useMemo(() => {
    const uploaded = documents.length;
    const validated = documents.filter((d) => d.status === "validated").length;
    const warning = documents.filter((d) => d.status === "warning").length;
    const rejected = documents.filter((d) => d.status === "rejected").length;
    return { uploaded, validated, warning, rejected };
  }, [documents]);

  const stats = [
    { label: "Uploaded documents", value: computed.uploaded, fillClass: "fill-blue" },
    { label: "Validated", value: computed.validated, fillClass: "fill-gold" },
    { label: "Warnings / Rejected", value: computed.warning + computed.rejected, fillClass: "fill-pending" },
  ];

  const latestUploads = documents.slice(0, 5).map((d, index) => ({
    key: d.id || `${d.name || "document"}-${d.createdAt || index}-${index}`,
    name: d.name || "Document",
    at: new Date(d.createdAt).toLocaleString(),
    status: d.status === "validated" ? "Validated" : d.status === "warning" ? "Warning" : "Rejected",
  }));

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-subtitle">
            {`Connected as ${user?.email || "user"}${user?.role ? ` (${user.role})` : ""}`}
          </p>
        </div>
        <div className="service-health">
          <span className={`health-dot ${apiHealth}`}></span>
          API: {apiHealth}
          <span className={`health-dot ${pyHealth}`} style={{ marginLeft: 12 }}></span>
          Python: {pyHealth}
        </div>
      </div>

      {dashboardLoading && <p className="empty-state">Loading dashboard data...</p>}
      {dashboardError && <p className="empty-state">{dashboardError}</p>}

      <div className="stats-grid">
        {stats.map((item) => (
          <div className="stat-card" key={item.label}>
            <div className="stat-top">
              <span className="stat-label">{item.label}</span>
            </div>
            <h2>{item.value}</h2>
            <div className="stat-bar">
              <div className={`stat-fill ${item.fillClass}`}></div>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-panel large-panel">
          <div className="panel-head">
            <h3>Recent Activity</h3>
            <span>•••</span>
          </div>

          <div className="activity-content">
            <div className="donut-wrapper">
              <div className="donut-chart">
                <div className="donut-inner">
                  <span>{computed.uploaded === 0 ? "0%" : `${Math.round((computed.validated / computed.uploaded) * 100)}%`}</span>
                  <p>Reviewed</p>
                </div>
              </div>
            </div>

            <div className="activity-legend">
              <div className="legend-item">
                <span className="legend-dot dot-uploaded"></span>
                <p>Uploaded</p>
                <strong>{computed.uploaded}</strong>
              </div>

              <div className="legend-item">
                <span className="legend-dot dot-validated"></span>
                <p>Validated</p>
                <strong>{computed.validated}</strong>
              </div>

              <div className="legend-item">
                <span className="legend-dot dot-pending"></span>
                <p>Warnings + Rejected</p>
                <strong>{computed.warning + computed.rejected}</strong>
              </div>
            </div>
          </div>

          <div className="chart-labels">
            <span>Mon</span>
            <span>Tue</span>
            <span>Wed</span>
            <span>Thu</span>
            <span>Fri</span>
            <span>Sat</span>
            <span>Sun</span>
          </div>
        </div>

        <div className="dashboard-panel small-panel">
          <div className="panel-head">
            <h3>Latest Uploads</h3>
            <span>•••</span>
          </div>

          {latestUploads.length === 0 && <p className="empty-state">No real activity yet.</p>}
          {latestUploads.map((upload) => (
            <div className="upload-item" key={upload.key}>
              <div>
                <strong>{upload.name}</strong>
                <p>{upload.at}</p>
              </div>
              <span className={`badge ${upload.status.toLowerCase()}`}>{upload.status}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}