import "../styles/adminDashboard.css";

export default function Dashboard() {
  return (
    <div className="admin-dashboard-page">
      <div className="admin-dashboard-header">
        <div>
          <h1 className="admin-dashboard-title">Admin Dashboard</h1>
          <p className="admin-dashboard-subtitle">
            Compliance and supplier monitoring overview.
          </p>
        </div>
      </div>

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="admin-stat-top">
            <span className="admin-stat-label">Suppliers</span>
          </div>
          <h2>24</h2>
          <div className="admin-stat-bar">
            <div className="admin-stat-fill fill-blue"></div>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-top">
            <span className="admin-stat-label">Pending validations</span>
          </div>
          <h2>7</h2>
          <div className="admin-stat-bar">
            <div className="admin-stat-fill fill-pending"></div>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-top">
            <span className="admin-stat-label">Alerts</span>
          </div>
          <h2>3</h2>
          <div className="admin-stat-bar">
            <div className="admin-stat-fill fill-gold"></div>
          </div>
        </div>
      </div>
    </div>
  );
}