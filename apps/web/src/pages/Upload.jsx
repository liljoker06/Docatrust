import "../styles/upload.css";
import "../styles/generation.css";
import { useState } from "react";
import { processOcr } from "../services/pyraApi";
import { addActivity } from "../lib/activity";
import { addDocument, normalizeDocumentFromOcr } from "../lib/documents";

export default function Upload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrError, setOcrError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setOcrResult(null);
      setOcrError(null);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }
    addActivity({ type: "upload", action: selectedFile.name, status: "success" });
    alert(`File selected: ${selectedFile.name}`);
  };

  const handleOcr = async () => {
    if (!selectedFile) return;
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);
    try {
      const data = await processOcr(selectedFile);
      setOcrResult(data);
      addDocument(normalizeDocumentFromOcr(data, selectedFile.name));
      addActivity({ type: "ocr", action: `upload OCR ${selectedFile.name}`, status: "success" });
    } catch (e) {
      setOcrError(e.message || "Erreur OCR");
      addActivity({ type: "ocr", action: `upload OCR ${selectedFile.name}`, status: "failed" });
    } finally {
      setOcrLoading(false);
    }
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

          {selectedFile && (
            <>
              <button
                className="upload-button"
                style={{ marginTop: 10, background: "linear-gradient(90deg, #5a8f5a, #7ab07a)" }}
                disabled={ocrLoading}
                onClick={handleOcr}
              >
                {ocrLoading ? "Traitement OCR…" : "Traiter avec OCR (Pyra)"}
              </button>
              {ocrError && <p className="ocr-error">{ocrError}</p>}
              {ocrResult && (
                <div className="generation-result" style={{ marginTop: 16 }}>
                  <div className="upload-card-head"><h3>Résultat OCR</h3></div>
                  <pre className="generation-output">
                    {JSON.stringify(ocrResult.data ?? ocrResult, null, 2)}
                  </pre>
                </div>
              )}
            </>
          )}
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