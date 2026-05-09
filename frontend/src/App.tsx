import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Flashcards } from './pages/Flashcards';
import { Study } from './pages/Study';
import { Analytics } from './pages/Analytics';
import { SimpleLogin } from './pages/SimpleLogin';
import axios from './lib/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) {
        setIsAuthenticated(false);
        return;
      }
      
      const response = await axios.get('/api/auth/me', {
        withCredentials: true
      });
      
      if (response.data) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      setIsAuthenticated(false);
      localStorage.removeItem('session_id');
      localStorage.removeItem('username');
    }
  };

  if (isAuthenticated === null) {
    return <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</Box>;
  }

  if (!isAuthenticated) {
    return (
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        <Routes>
          <Route path="/login" element={<SimpleLogin />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/flashcards" element={<Flashcards />} />
          <Route path="/study" element={<Study />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default App;
