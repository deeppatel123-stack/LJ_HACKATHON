// client/src/App.jsx

import { useState } from 'react';
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

  const handleLogin = async (e) => {
    e.preventDefault();
    if (username && password) {
      setIsAuthenticated(true);
      await fetchDocuments();
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
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleSearch = async (searchQuery) => {
    try {
      const response = await fetch(`${API_BASE_URL}/search/?query=${searchQuery}&username=${username}&password=${password}`);
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        {isRegistering ? (
          <UserRegistration />
        ) : (
          <form onSubmit={handleLogin} className="login-form">
            <h2>Login to Document Hub</h2>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
          </form>
        )}
        <button onClick={() => setIsRegistering(!isRegistering)}>
          {isRegistering ? 'Back to Login' : 'Register a new user'}
        </button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header>
        <h1>AI-Powered Document Hub</h1>
        <button onClick={handleLogout}>Logout</button>
      </header>
      <DocumentUpload username={username} password={password} onUploadSuccess={fetchDocuments} />
      <div className="controls-container">
        <SearchBar onSearch={handleSearch} />
        <button onClick={fetchDocuments} className="refresh-button">Refresh Documents</button>
      </div>
      <DocumentList documents={documents} />
    </div>
  );
}

export default App;