// client/src/components/DocumentUpload.jsx

import { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8002';

const DocumentUpload = ({ username, password, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    setLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Success: ${data.message}`);
        onUploadSuccess();
      } else {
        setMessage(`Error: ${data.detail || 'Upload failed'}`);
      }
    } catch (error) {
      setMessage('Error: Failed to connect to server.',error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h3>Upload a New Document</h3>
      <form onSubmit={handleUpload}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload & Classify'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default DocumentUpload;