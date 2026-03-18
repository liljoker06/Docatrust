import { useState } from "react";

export default function FileUpload() {
  const [file, setFile] = useState(null);

  const handleUpload = () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    alert(`File selected: ${file.name}`);
  };

  return (
    <div
      style={{
        background: "#fff",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        maxWidth: "500px",
      }}
    >
      <h3>Upload a document</h3>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        style={{ marginTop: "10px", marginBottom: "20px" }}
      />

      <br />

      <button
        onClick={handleUpload}
        style={{
          background: "#2563eb",
          color: "#fff",
          border: "none",
          padding: "10px 18px",
          borderRadius: "8px",
          cursor: "pointer",
        }}
      >
        Upload
      </button>
    </div>
  );
}