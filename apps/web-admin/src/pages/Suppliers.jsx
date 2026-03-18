import { Link } from "react-router-dom";
import Table from "../components/Table";

export default function Suppliers() {
  const columns = [
    { key: "name", label: "Name" },
    { key: "status", label: "Status" },
    { key: "country", label: "Country" },
  ];

  const data = [
    { id: 1, name: "Supplier A", status: "Validated", country: "France" },
    { id: 2, name: "Supplier B", status: "Pending", country: "Morocco" },
    { id: 3, name: "Supplier C", status: "Rejected", country: "Spain" },
  ];

  return (
    <div>
      <h1>Suppliers</h1>
      <Table columns={columns} data={data} />

      <h3>Open details</h3>
      {data.map((supplier) => (
        <div key={supplier.id}>
          <Link to={`/suppliers/${supplier.id}`}>{supplier.name}</Link>
        </div>
      ))}
    </div>
  );
}