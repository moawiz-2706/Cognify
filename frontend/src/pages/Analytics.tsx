import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import axios from '../lib/api';
import toast from 'react-hot-toast';

interface LearningAnalytics {
  user_id: number;
  total_cards: number;
  mastered_cards: number;
  learning_cards: number;
  review_cards: number;
  average_accuracy: number;
  study_streak: number;
  last_study_date: string | null;
  performance_trend: number[];
}

export const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<LearningAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

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
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  if (!analytics) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" sx={{ mb: 2 }}>
          No Analytics Available
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Start studying to see your learning analytics!
        </Typography>
      </Box>
    );
  }

  const masteryPercentage = analytics.total_cards > 0 
    ? (analytics.mastered_cards / analytics.total_cards) * 100 
    : 0;

  const cardStatusData = [
    { name: 'Mastered', value: analytics.mastered_cards, color: '#00C49F' },
    { name: 'Learning', value: analytics.learning_cards, color: '#FFBB28' },
    { name: 'Review', value: analytics.review_cards, color: '#0088FE' },
  ];

  const performanceData = analytics.performance_trend.map((value, index) => ({
    day: `Day ${index + 1}`,
    accuracy: value * 100,
  }));

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Learning Analytics
        </Typography>
        <Tooltip title="Refresh Analytics">
          <IconButton onClick={fetchAnalytics} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Total Cards
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {analytics.total_cards}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Mastery Rate
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {Math.round(masteryPercentage)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={masteryPercentage}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Average Accuracy
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                {Math.round(analytics.average_accuracy * 100)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Study Streak
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'secondary.main' }}>
                {analytics.study_streak}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Card Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Card Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={cardStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {cardStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Performance Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#8884d8"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Learning Progress */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Learning Progress
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                      {analytics.mastered_cards}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Mastered Cards
                    </Typography>
                    <Chip
                      label="Completed"
                      color="success"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                      {analytics.learning_cards}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Learning Cards
                    </Typography>
                    <Chip
                      label="In Progress"
                      color="warning"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                      {analytics.review_cards}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Review Cards
                    </Typography>
                    <Chip
                      label="Due for Review"
                      color="info"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
