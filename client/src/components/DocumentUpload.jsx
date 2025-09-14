// client/src/components/DocumentUpload.jsx

import { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8002';

const DocumentUpload = ({ username, password, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setUploadMessage('');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setUploadMessage('Please select a file to upload.');
      return;
    }

    setUploading(true);
    setUploadMessage('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadMessage('Document uploaded and processed successfully!');
        setFile(null);
        // Reset file input
        e.target.reset();
        // Refresh documents list
        if (onUploadSuccess) onUploadSuccess();
      } else {
        const errorData = await response.json();
        setUploadMessage(`Upload failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setUploadMessage(`Upload error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h3>Upload Document</h3>
      <p>Upload PDF, DOCX, or TXT files for automatic classification and indexing</p>
      
      <form onSubmit={handleUpload}>
        <div className="file-input-wrapper">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="file-input"
            disabled={uploading}
          />
          {file && (
            <div className="file-preview">
              <span>Selected: {file.name}</span>
              <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>
        
        <button 
          type="submit" 
          className="upload-button"
          disabled={uploading || !file}
        >
          {uploading ? (
            <>
              <span className="loading"></span>
              Processing...
            </>
          ) : (
            'Upload & Process'
          )}
        </button>
      </form>

      {uploadMessage && (
        <div className={`upload-message ${uploadMessage.includes('successfully') ? 'success-message' : 'error-message'}`}>
          {uploadMessage}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;