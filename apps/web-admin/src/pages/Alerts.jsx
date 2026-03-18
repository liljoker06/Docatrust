import StatusBadge from "../components/StatusBadge";

export default function Alerts() {
  const alerts = [
    { id: 1, message: "Expired KBIS document", status: "High" },
    { id: 2, message: "Missing tax certificate", status: "Medium" },
    { id: 3, message: "Unreadable invoice upload", status: "Low" },
  ];

  return (
    <div>
      <h1>Alerts</h1>

      {alerts.map((alert) => (
        <div key={alert.id}>
          <p>{alert.message} - <StatusBadge status={alert.status} /></p>
        </div>
      ))}
    </div>
  );
}