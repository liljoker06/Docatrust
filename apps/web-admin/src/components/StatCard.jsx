export default function StatCard({ title, value }) {
  return (
    <div style={{ border: "1px solid #ccc", padding: "16px", marginBottom: "12px" }}>
      <h3>{value}</h3>
      <p>{title}</p>
    </div>
  );
}