import { useParams } from "react-router-dom";

export default function SupplierDetails() {
  const { id } = useParams();

  return (
    <div>
      <h1>Supplier Details</h1>
      <p>Supplier ID: {id}</p>
      <p>Name: Supplier {id}</p>
      <p>Status: Pending</p>
      <p>Last document: KBIS.pdf</p>
    </div>
  );
}