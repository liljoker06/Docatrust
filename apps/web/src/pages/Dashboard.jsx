import "../styles/dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-subtitle">
            Welcome to the DocaTrust user dashboard.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">Uploaded documents</span>
          </div>
          <h2>12</h2>
          <div className="stat-bar">
            <div className="stat-fill fill-blue"></div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">Validated documents</span>
          </div>
          <h2>8</h2>
          <div className="stat-bar">
            <div className="stat-fill fill-gold"></div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">Pending review</span>
          </div>
          <h2>4</h2>
          <div className="stat-bar">
            <div className="stat-fill fill-pending"></div>
          </div>
        </div>
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
                  <span>67%</span>
                  <p>Reviewed</p>
                </div>
              </div>
            </div>

            <div className="activity-legend">
              <div className="legend-item">
                <span className="legend-dot dot-uploaded"></span>
                <p>Uploaded</p>
                <strong>12</strong>
              </div>

              <div className="legend-item">
                <span className="legend-dot dot-validated"></span>
                <p>Validated</p>
                <strong>8</strong>
              </div>

              <div className="legend-item">
                <span className="legend-dot dot-pending"></span>
                <p>Pending</p>
                <strong>4</strong>
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

          <div className="upload-item">
            <div>
              <strong>Invoice_2026_01.pdf</strong>
              <p>Today, 11:30 AM</p>
            </div>
            <span className="badge validated">Validated</span>
          </div>

          <div className="upload-item">
            <div>
              <strong>Supplier_Kbis.pdf</strong>
              <p>Today, 11:30 AM</p>
            </div>
            <span className="badge pending">Pending</span>
          </div>

          <div className="upload-item">
            <div>
              <strong>RIB_company.pdf</strong>
              <p>Today, 11:30 AM</p>
            </div>
            <span className="badge rejected">Rejected</span>
          </div>
        </div>
      </div>
    </div>
  );
}