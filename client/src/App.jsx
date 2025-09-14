import { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import SearchBar from './components/SearchBar';
import UserRegistration from './components/UserRegistration';
import './App.css'; 

const API_BASE_URL = 'http://127.0.0.1:8002';

function App() {
  const [documents, setDocuments] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [fetchError, setFetchError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchDocuments();
    }
  }, [isAuthenticated]);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (username && password) {
      // Assuming a successful login for now as we don't have a login endpoint
      setIsAuthenticated(true);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername('');
    setPassword('');
    setDocuments([]);
  };

  const fetchDocuments = async () => {
    try {
      console.log('Fetching documents for user:', username);
      console.log('API URL:', `${API_BASE_URL}/documents/?username=${username}&password=${password}`);
      
      const response = await fetch(`${API_BASE_URL}/documents/?username=${username}&password=${password}`);
      console.log('Fetch response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Fetched documents:', data);
        setDocuments(data);
        setFetchError('');
      } else {
        const errorText = await response.text();
        console.error('Fetch failed:', response.status, errorText);
        setFetchError(`Failed to fetch documents. Status: ${response.status}`);
        setDocuments([]);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setFetchError('Error fetching documents: ' + error.message);
    }
  };

  const handleSearch = async (searchQuery) => {
    try {
      console.log('Searching for:', searchQuery);
      console.log('API URL:', `${API_BASE_URL}/search/?query=${searchQuery}&username=${username}&password=${password}`);
      
      const response = await fetch(`${API_BASE_URL}/search/?query=${searchQuery}&username=${username}&password=${password}`);
      console.log('Search response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Search results:', data);
        setDocuments(data);
        setFetchError('');
      } else {
        const errorText = await response.text();
        console.error('Search failed:', response.status, errorText);
        setFetchError(`Failed to search documents. Status: ${response.status}`);
        setDocuments([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setFetchError('Error searching documents: ' + error.message);
    }
  };

  const handleDelete = async (id) => {
    try {
      console.log('Deleting document:', id);
      console.log('API URL:', `${API_BASE_URL}/documents/${id}/?username=${username}&password=${password}`);
      
      const response = await fetch(`${API_BASE_URL}/documents/${id}/?username=${username}&password=${password}`, {
        method: 'DELETE',
      });
      console.log('Delete response status:', response.status);
      
      if (response.ok) {
        console.log('Document deleted successfully');
        fetchDocuments();
      } else {
        const errorText = await response.text();
        console.error('Delete failed:', response.status, errorText);
        setFetchError(`Failed to delete document. Status: ${response.status}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      setFetchError('Error deleting document: ' + error.message);
    }
  };

  const handleDeleteAllDocuments = async () => {
    if (!window.confirm('This will delete ALL documents from the database. Are you sure?')) {
      return;
    }
    
    try {
      console.log('Deleting all documents...');
      const response = await fetch(`${API_BASE_URL}/force-cleanup-all-documents/?username=${username}&password=${password}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Delete all successful:', result.message);
        alert('All documents have been deleted successfully.');
        fetchDocuments();
      } else {
        const errorText = await response.text();
        console.error('Delete all failed:', response.status, errorText);
        setFetchError(`Failed to delete all documents. Status: ${response.status}`);
      }
    } catch (error) {
      console.error('Delete all error:', error);
      setFetchError('Error deleting all documents: ' + error.message);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <h1 className="main-title">AI-Powered Document Hub</h1>
        {isRegistering ? (
          <UserRegistration />
        ) : (
          <form onSubmit={handleLogin} className="auth-form">
            <h2>Login</h2>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="auth-input"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
            />
            <button type="submit" className="auth-button">Login</button>
          </form>
        )}
        <button onClick={() => setIsRegistering(!isRegistering)} className="toggle-auth-button">
          {isRegistering ? 'Back to Login' : 'Register a new user'}
        </button>
        {fetchError && <p className="error-message">{fetchError}</p>}
      </div>
    );
  }

  return (
    <div className="app-container">
      <header>
        <h1 className="main-title">AI-Powered Document Hub</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </header>
      <main>
        <section className="section-upload">
          <DocumentUpload username={username} password={password} onUploadSuccess={fetchDocuments} />
        </section>
        <section className="section-controls">
          <SearchBar onSearch={handleSearch} />
          <button onClick={fetchDocuments} className="refresh-button">Refresh Documents</button>
          {username === 'admin' && (
            <button onClick={handleDeleteAllDocuments} className="delete-all-button">Delete All Documents</button>
          )}
        </section>
        <section className="section-documents">
          <DocumentList documents={documents} onDelete={handleDelete} />
        </section>
      </main>
      {fetchError && <p className="error-message">{fetchError}</p>}
    </div>
  );
}

export default App;