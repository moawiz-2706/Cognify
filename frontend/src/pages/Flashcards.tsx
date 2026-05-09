import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Fab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  MoreVert,
  School,
  Schedule,
  CheckCircle,
  Quiz,
} from '@mui/icons-material';
import axios from '../lib/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { FlashcardCreator } from '../components/FlashcardCreator';
import { FlashcardTemplates } from '../components/FlashcardTemplates';
import { DegreeSemesterSelector } from '../components/DegreeSemesterSelector';

interface Flashcard {
  id: number;
  front: string;
  back: string;
  tags: string[];
  difficulty: string;
  status: string;
  difficulty_score: number;
  next_review_time: string | null;
  review_count: number;
  correct_count: number;
  created_at: string;
  updated_at: string;
}

interface FlashcardForm {
  front: string;
  back: string;
  tags: string;
  difficulty: string;
}

export const Flashcards: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [creatorOpen, setCreatorOpen] = useState(false);
  const [templatesOpen, setTemplatesOpen] = useState(false);
  const [editingCard, setEditingCard] = useState<Flashcard | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCard, setSelectedCard] = useState<Flashcard | null>(null);

  useEffect(() => {
    fetchFlashcards();
    
    // Listen for flashcard updates
    const handleFlashcardsUpdated = () => {
      console.log('Flashcards updated event received, refreshing...');
      fetchFlashcards();
    };
    
    window.addEventListener('flashcardsUpdated', handleFlashcardsUpdated);
    
    // Also refresh when page becomes visible
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchFlashcards();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      window.removeEventListener('flashcardsUpdated', handleFlashcardsUpdated);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const fetchFlashcards = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/flashcards/', {
        withCredentials: true
      });
      const fetchedCards = response.data || [];
      console.log('Fetched flashcards:', fetchedCards.length);
      setFlashcards(fetchedCards);
      if (fetchedCards.length === 0) {
        console.log('No flashcards found. Make sure you have:');
        console.log('1. Selected a degree program');
        console.log('2. Selected a semester');
        console.log('3. Added courses from that semester');
        toast('No flashcards yet. Select courses to generate flashcards!', {
          icon: 'ℹ️',
          duration: 5000
        });
      } else {
        console.log(`Successfully loaded ${fetchedCards.length} flashcards`);
      }
    } catch (error: any) {
      console.error('Error fetching flashcards:', error);
      toast.error('Failed to load flashcards');
      setFlashcards([]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreator = (card?: Flashcard) => {
    if (card) {
      setEditingCard(card);
    } else {
      setEditingCard(null);
    }
    setCreatorOpen(true);
  };

  const handleCloseCreator = () => {
    setCreatorOpen(false);
    setEditingCard(null);
  };

  const handleCreatorSubmit = async (data: any) => {
    try {
      // Validate required fields before sending
      if (!data.question || !data.question.trim()) {
        toast.error('Question is required');
        return;
      }
      if (!data.answer || !data.answer.trim()) {
        toast.error('Answer is required');
        return;
      }
      if (!data.subject || !data.subject.trim()) {
        toast.error('Subject is required');
        return;
      }

      const cardData = {
        front: data.question.trim(),
        back: data.answer.trim(),
        tags: data.tags || [],
        difficulty: data.difficulty || 'medium',
        subject: data.subject.trim() || null,
        topic: data.topic?.trim() || null,
      };

      // Double-check before sending
      if (!cardData.front || !cardData.back) {
        toast.error('Question and Answer are required');
        return;
      }

      if (editingCard) {
        const response = await axios.put(`/api/flashcards/${editingCard.id}`, cardData);
        toast.success('Flashcard updated successfully');
      } else {
        const response = await axios.post('/api/flashcards/', cardData);
        toast.success('Flashcard created successfully');
      }

      fetchFlashcards();
      handleCloseCreator();
      
      // Trigger analytics refresh event for other pages
      window.dispatchEvent(new CustomEvent('flashcardsUpdated'));
    } catch (error: any) {
      console.error('Error saving flashcard:', error);
      let errorMessage = 'Failed to save flashcard';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          errorMessage = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = error.response.data.message || JSON.stringify(detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`/api/flashcards/${id}`);
      toast.success('Flashcard deleted successfully');
      fetchFlashcards();
    } catch (error) {
      toast.error('Failed to delete flashcard');
    }
    setAnchorEl(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'mastered':
        return 'success';
      case 'learning':
        return 'warning';
      case 'review':
        return 'info';
      default:
        return 'default';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Degree and Semester Selector */}
      <DegreeSemesterSelector />

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            My Flashcards
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create and manage your study cards
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Quiz />}
            onClick={() => setTemplatesOpen(true)}
            size="large"
          >
            Use Template
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenCreator()}
            size="large"
          >
            Create New Card
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {flashcards.map((card) => (
          <Grid item xs={12} sm={6} md={4} key={card.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
                    {card.front}
                  </Typography>
                  <IconButton
                    onClick={(e) => {
                      setAnchorEl(e.currentTarget);
                      setSelectedCard(card);
                    }}
                  >
                    <MoreVert />
                  </IconButton>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {card.back}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip
                    label={card.status}
                    color={getStatusColor(card.status)}
                    size="small"
                  />
                  <Chip
                    label={card.difficulty}
                    color={getDifficultyColor(card.difficulty)}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                {card.tags && card.tags.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {card.tags.map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                )}

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 'auto' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <School fontSize="small" color="action" />
                    <Typography variant="caption">
                      {card.review_count} reviews
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <CheckCircle fontSize="small" color="action" />
                    <Typography variant="caption">
                      {Math.round((card.correct_count / Math.max(card.review_count, 1)) * 100)}% accuracy
                    </Typography>
                  </Box>
                </Box>

                {card.next_review_time && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                    <Schedule fontSize="small" color="action" />
                    <Typography variant="caption">
                      Next: {format(new Date(card.next_review_time), 'MMM dd, HH:mm')}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => {
          if (selectedCard) {
            handleOpenCreator(selectedCard);
          }
          setAnchorEl(null);
        }}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedCard) {
            handleDelete(selectedCard.id);
          }
        }}>
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Flashcard Creator */}
      <FlashcardCreator
        open={creatorOpen}
        onClose={handleCloseCreator}
        onSubmit={handleCreatorSubmit}
        editingCard={editingCard}
      />

      {/* Flashcard Templates */}
      <FlashcardTemplates
        open={templatesOpen}
        onClose={() => setTemplatesOpen(false)}
        onSelectTemplate={(template) => {
          // Pre-fill the creator with template data
          // First, get the first available course code as subject
          const firstCourse = flashcards.length > 0 && flashcards[0].tags && flashcards[0].tags.length > 0 
            ? flashcards[0].tags[0] 
            : 'general';
          
          setEditingCard({
            id: 0,
            front: template.examples[0] || '',
            back: '',
            tags: [template.id],
            difficulty: 'medium',
            subject: firstCourse,
            topic: template.name,
          } as any);
          setTemplatesOpen(false);
          setCreatorOpen(true);
        }}
      />

      {/* Floating Action Button for quick access */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={() => handleOpenCreator()}
      >
        <Add />
      </Fab>
    </Box>
  );
};
