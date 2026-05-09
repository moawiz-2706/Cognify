import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  School,
  Quiz,
  TrendingUp,
  Schedule,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from '../lib/api';
import toast from 'react-hot-toast';

interface DashboardStats {
  total_cards: number;
  mastered_cards: number;
  learning_cards: number;
  review_cards: number;
  average_accuracy: number;
  study_streak: number;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalytics();
    
    // Refresh analytics when flashcards are updated
    const handleFlashcardsUpdated = () => {
      fetchAnalytics();
    };
    
    // Refresh analytics when page becomes visible
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchAnalytics();
      }
    };
    
    // Refresh on focus
    const handleFocus = () => {
      fetchAnalytics();
    };
    
    window.addEventListener('flashcardsUpdated', handleFlashcardsUpdated);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    
    // Refresh every 3 seconds to catch updates
    const interval = setInterval(() => {
      fetchAnalytics();
    }, 3000);
    
    return () => {
      window.removeEventListener('flashcardsUpdated', handleFlashcardsUpdated);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
      clearInterval(interval);
    };
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/api/analytics/learning');
      setStats(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = () => {
    if (!stats || stats.total_cards === 0) return 0;
    return (stats.mastered_cards / stats.total_cards) * 100;
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <School color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Cards</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {stats?.total_cards || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Mastered</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {stats?.mastered_cards || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Quiz color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Learning</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {stats?.learning_cards || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Schedule color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Due for Review</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {stats?.review_cards || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Section */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Learning Progress
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Mastery Progress</Typography>
                  <Typography variant="body2">
                    {Math.round(getProgressPercentage())}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getProgressPercentage()}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`${stats?.average_accuracy ? Math.round(stats.average_accuracy * 100) : 0}% Accuracy`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`${stats?.study_streak || 0} Day Streak`}
                  color="secondary"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => navigate('/study')}
                  startIcon={<Quiz />}
                >
                  Start Studying
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/flashcards')}
                  startIcon={<School />}
                >
                  Manage Cards
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/analytics')}
                  startIcon={<TrendingUp />}
                >
                  View Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
