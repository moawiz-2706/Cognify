import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Flashcards } from './pages/Flashcards';
import { Study } from './pages/Study';
import { Analytics } from './pages/Analytics';

function SimpleApp() {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/flashcards" element={<Flashcards />} />
          <Route path="/study" element={<Study />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default SimpleApp;
