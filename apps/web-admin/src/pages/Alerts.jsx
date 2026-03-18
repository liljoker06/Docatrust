import StatusBadge from "../components/StatusBadge";
import "../styles/alerts.css";

export default function Alerts() {
  const alerts = [
    { id: 1, message: "Expired KBIS document", status: "High" },
    { id: 2, message: "Missing tax certificate", status: "Medium" },
    { id: 3, message: "Unreadable invoice upload", status: "Low" },
  ];

  return (
    <div className="alerts-page">
      {/* HEADER */}
      <div className="alerts-header">
        <h1 className="alerts-title">Alerts</h1>
        <p className="alerts-subtitle">
          Monitor compliance issues and document problems.
        </p>
      </div>

      {/* ALERTS PANEL */}
      <div className="alerts-panel">
        <div className="panel-head">
          <h3>Recent Alerts</h3>
          <span>•••</span>
        </div>

        <div className="alerts-list">
          {alerts.map((alert) => (
            <div key={alert.id} className="alert-card">
              <div className="alert-info">
                <strong>{alert.message}</strong>
                <p>Alert #{alert.id}</p>
              </div>

              <StatusBadge status={alert.status} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}