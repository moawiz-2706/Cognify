import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../lib/api';
import toast from 'react-hot-toast';

export const SimpleLogin: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isRegister) {
        // Register - use JSON
        if (!username || !username.trim()) {
          setError('Username is required');
          toast.error('Username is required');
          return;
        }
        if (!password || password.length < 3) {
          setError('Password must be at least 3 characters');
          toast.error('Password must be at least 3 characters');
          return;
        }
        
        await axios.post('/api/auth/register', {
          username: username.trim(),
          password: password,
          email: ''
        }, {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        });
        toast.success('Registration successful! Please login.');
        setIsRegister(false);
        setUsername('');
        setPassword('');
      } else {
        // Login - use JSON
        const response = await axios.post('/api/auth/login', {
          username: username,
          password: password
        }, {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        });
        
        // Store session ID and username
        if (response.data.session_id) {
          localStorage.setItem('session_id', response.data.session_id);
          localStorage.setItem('username', response.data.username || username);
        }
        
        toast.success('Login successful!');
        window.location.href = '/dashboard';  // Full reload to refresh auth state
      }
    } catch (error: any) {
      let errorMsg = 'Login failed';
      
      if (error.response?.data) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          errorMsg = detail.map((err: any) => {
            if (typeof err === 'string') return err;
            if (err.msg) return err.msg;
            return JSON.stringify(err);
          }).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (typeof detail === 'object') {
          // Handle object errors
          errorMsg = detail.message || detail.msg || JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Card sx={{ width: '100%', p: 3 }}>
          <CardContent>
            <Typography component="h1" variant="h4" align="center" gutterBottom>
              {isRegister ? 'Register' : 'Login'}
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
              {isRegister 
                ? 'Create a new account to start learning'
                : 'Welcome to Cognify - Adaptive Learning Assistant'
              }
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? 'Please wait...' : (isRegister ? 'Register' : 'Login')}
              </Button>
              <Button
                fullWidth
                variant="text"
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError('');
                }}
              >
                {isRegister 
                  ? 'Already have an account? Login'
                  : "Don't have an account? Register"
                }
              </Button>
            </Box>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="caption" display="block" gutterBottom>
                <strong>Demo Accounts:</strong>
              </Typography>
              <Typography variant="caption" display="block">
                Username: <strong>admin</strong> / Password: <strong>admin123</strong>
              </Typography>
              <Typography variant="caption" display="block">
                Username: <strong>student</strong> / Password: <strong>student123</strong>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

