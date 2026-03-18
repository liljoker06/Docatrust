import "../styles/upload.css";
import { useState } from "react";

export default function Upload() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    alert(`File selected: ${selectedFile.name}`);
  };

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1 className="upload-title">Upload Document</h1>
        <p className="upload-subtitle">
          Add your files securely for verification and follow their status.
        </p>
      </div>

      <div className="upload-grid">
        <div className="upload-card">
          <div className="upload-card-head">
            <h3>Select a File</h3>
            <span>•••</span>
          </div>

          <label className="upload-dropzone">
            <input type="file" onChange={handleFileChange} />
            <div className="upload-dropzone-content">
              <div className="upload-icon">↑</div>
              <h4>Drag & drop your file here</h4>
              <p>or click to browse from your computer</p>
            </div>
          </label>

          {selectedFile && (
            <div className="selected-file">
              <strong>Selected file:</strong>
              <span>{selectedFile.name}</span>
            </div>
          )}

          <button className="upload-button" onClick={handleUpload}>
            Upload Document
          </button>
        </div>

        <div className="upload-side-card">
          <div className="upload-card-head">
            <h3>Upload Tips</h3>
            <span>•••</span>
          </div>

          <ul className="upload-tips">
            <li>Use PDF, PNG, or JPG files.</li>
            <li>Make sure the document is readable.</li>
            <li>Upload invoices, KBIS, or RIB documents.</li>
            <li>Track validation in the dashboard after upload.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}