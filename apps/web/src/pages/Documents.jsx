export default function DocumentCard({ title, status, date }) {
  return (
    <div
      style={{
        background: "#fff",
        padding: "16px",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        marginBottom: "16px",
      }}
    >
      <h4 style={{ margin: "0 0 8px 0" }}>{title}</h4>
      <p style={{ margin: "4px 0" }}>
        <strong>Status:</strong> {status}
      </p>
      <p style={{ margin: "4px 0" }}>
        <strong>Date:</strong> {date}
      </p>
    </div>
  );
}