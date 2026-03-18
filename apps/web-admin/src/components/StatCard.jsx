export default function StatCard({ title, value, fillClass }) {
  return (
    <div className="stat-card">
      <p className="stat-label">{title}</p>
      <h2>{value}</h2>

      <div className="stat-bar">
        <div className={`stat-fill ${fillClass}`}></div>
      </div>
    </div>
  );
}