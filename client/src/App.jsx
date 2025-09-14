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
      const response = await fetch(`${API_BASE_URL}/documents/?username=${username}&password=${password}`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
        setFetchError('');
      } else {
        setFetchError('Failed to fetch documents. Check your credentials.');
        setDocuments([]);
      }
    } catch (error) {
      setFetchError('Error fetching documents: ' + error.message);
    }
  };

  const handleSearch = async (searchQuery) => {
    try {
      const response = await fetch(`${API_BASE_URL}/search/?query=${searchQuery}&username=${username}&password=${password}`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
        setFetchError('');
      } else {
        setFetchError('Failed to search documents. Check your credentials.');
        setDocuments([]);
      }
    } catch (error) {
      setFetchError('Error searching documents: ' + error.message);
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
        </section>
        <section className="section-documents">
          <DocumentList documents={documents} />
        </section>
      </main>
      {fetchError && <p className="error-message">{fetchError}</p>}
    </div>
  );
}

export default App;