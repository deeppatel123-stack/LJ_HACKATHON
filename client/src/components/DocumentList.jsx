// client/src/components/DocumentList.jsx

const DocumentList = ({ documents }) => {
  return (
    <div className="document-list-container">
      <h3>Documents</h3>
      {documents.length > 0 ? (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id} className="document-item">
              <p><strong>Filename:</strong> {doc.filename}</p>
              <p><strong>Category:</strong> {doc.category}</p>
              <p><strong>Title:</strong> {doc.title}</p>
              <p><strong>Summary:</strong> {doc.summary}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No documents found.</p>
      )}
    </div>
  );
};

export default DocumentList;