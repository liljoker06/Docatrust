import "../styles/logs.css";

export default function Logs() {
  const logs = [
    "2026-03-16 10:00 - Supplier A document uploaded",
    "2026-03-16 10:15 - Validation started",
    "2026-03-16 10:22 - Alert generated for Supplier B",
  ];

  return (
    <div className="logs-page">
      <div className="logs-header">
        <h1 className="logs-title">Logs</h1>
        <p className="logs-subtitle">
          Track recent system and compliance activity.
        </p>
      </div>

      <div className="logs-panel">
        <div className="logs-panel-head">
          <h3>Recent Activity</h3>
          <span>•••</span>
        </div>

        <div className="logs-list">
          {logs.map((log, index) => {
            const [datePart, messagePart] = log.split(" - ");
            return (
              <div key={index} className="log-card">
                <div className="log-time">{datePart}</div>
                <div className="log-message">{messagePart}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}