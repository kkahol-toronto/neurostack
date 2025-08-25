import React, { useState, useEffect } from 'react';
import { CssBaseline } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import DecisionDocumentation from './components/DecisionDocumentation';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogin = (token: string, userData: any) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <div className="App">
      <CssBaseline />
      <Router>
        <Routes>
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Dashboard onLogout={handleLogout} user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <Login onLogin={handleLogin} />
              )
            } 
          />
          <Route 
            path="/decision-documentation" 
            element={
              isAuthenticated ? (
                <DecisionDocumentation />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
