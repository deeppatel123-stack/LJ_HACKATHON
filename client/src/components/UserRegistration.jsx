import React, { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8002'; // or your port

const UserRegistration = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('HR');
  const [registering, setRegistering] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setMessage('Please fill in all fields.');
      return;
    }

    setRegistering(true);
    setMessage('');

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('role', role);

    try {
      const response = await fetch(`${API_BASE_URL}/register/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setMessage('Registration successful! You can now login.');
        setUsername('');
        setPassword('');
        setRole('HR');
      } else {
        const errorData = await response.json();
        setMessage(`Registration failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setMessage(`Registration error: ${error.message}`);
    } finally {
      setRegistering(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>Create Account</h2>
      <p style={{textAlign: 'center', marginBottom: '1.5rem', color: '#666'}}>
        Join the AI-Powered Document Hub
      </p>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="auth-input"
          disabled={registering}
        />
        
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="auth-input"
          disabled={registering}
        />
        
        <div className="role-selection">
          <label style={{display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#333'}}>
            Select Your Role:
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="auth-input"
            disabled={registering}
            style={{appearance: 'none', backgroundImage: 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3e%3cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'M6 8l4 4 4-4\'/%3e%3c/svg%3e")', backgroundPosition: 'right 0.5rem center', backgroundRepeat: 'no-repeat', backgroundSize: '1.5em 1.5em', paddingRight: '2.5rem'}}
          >
            <option value="HR">HR - Human Resources</option>
            <option value="Finance">Finance - Financial Documents</option>
            <option value="Legal">Legal - Legal Documents</option>
            <option value="Admin">Admin - Full Access</option>
          </select>
        </div>
        
        <button 
          type="submit" 
          className="auth-button"
          disabled={registering}
        >
          {registering ? (
            <>
              <span className="loading"></span>
              Creating Account...
            </>
          ) : (
            'Register'
          )}
        </button>
      </form>

      {message && (
        <div className={`upload-message ${message.includes('successful') ? 'success-message' : 'error-message'}`}>
          {message}
        </div>
      )}
      
      <div style={{marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem', color: '#666'}}>
        <p>Your account will have access to documents based on your selected role</p>
      </div>
    </div>
  );
};

export default UserRegistration;