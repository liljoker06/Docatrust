export default function Logs() {
  const logs = [
    "2026-03-16 10:00 - Supplier A document uploaded",
    "2026-03-16 10:15 - Validation started",
    "2026-03-16 10:22 - Alert generated for Supplier B",
  ];

  return (
    <div>
      <h1>Logs</h1>

      {logs.map((log, index) => (
        <p key={index}>{log}</p>
      ))}
    </div>
  );
}