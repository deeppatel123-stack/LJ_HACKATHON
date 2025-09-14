import React, { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8002'; // or your port

const UserRegistration = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('HR'); // Default role
  const [message, setMessage] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
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

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
      } else {
        setMessage(`Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage('Network error. Failed to connect to server.', error );
    }
  };

  return (
    <div className="registration-container">
      <h3>Register a New User</h3>
      <form onSubmit={handleRegister} className="registration-form">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="HR">HR</option>
          <option value="Finance">Finance</option>
          <option value="Admin">Admin</option>
          <option value="Legal">Legal</option>
          {/* Add all your roles here */}
        </select>
        <button type="submit">Register</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default UserRegistration;