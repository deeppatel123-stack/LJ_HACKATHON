// client/src/components/DocumentList.jsx

const DocumentList = ({ documents, onDelete }) => {
  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await onDelete(docId);
      } catch (error) {
        alert('Failed to delete document: ' + error.message);
      }
    }
  };

  const formatUploadDate = (dateString) => {
    try {
      if (!dateString || dateString === 'None' || dateString === '' || dateString.length < 10) {
        return 'Date unavailable';
      }
      
      const date = new Date(dateString);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Date unavailable';
      }
      
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      return 'Date unavailable';
    }
  };

  return (
    <div className="document-list-container">
      <h3>Document Library</h3>
      {documents.length > 0 ? (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id} className="document-item">
              <button 
                className="delete-button"
                onClick={() => handleDelete(doc.id)}
                title="Delete Document"
              >
                Delete
              </button>
              
              <div className="document-details">
                <p><strong>Filename:</strong> {doc.filename}</p>
                <p><strong>Category:</strong> {doc.category}</p>
                <p><strong>Author:</strong> {doc.author}</p>
                <p><strong>Uploaded:</strong> {formatUploadDate(doc.upload_date)}</p>
                <p><strong>Summary:</strong> {doc.summary}</p>
                {doc.search_score && (
                  <p><strong>Relevance Score:</strong> {(doc.search_score * 100).toFixed(1)}%</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="no-documents">
          <p>No documents found.</p>
          <p>Upload your first document to get started!</p>
        </div>
      )}
    </div>
  );
};

export default DocumentList;