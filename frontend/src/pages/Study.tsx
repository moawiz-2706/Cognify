import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  LinearProgress,
  Chip,
  Alert,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Timer,
  School,
  Send,
  Visibility,
  VisibilityOff,
  PlayArrow,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import axios from '../lib/api';
import toast from 'react-hot-toast';

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
  subject?: string;
  topic?: string;
}

interface StudySession {
  currentCard: Flashcard | null;
  startTime: number;
  sessionCards: Flashcard[];
  completedCards: number;
  totalCards: number;
  selectedSubjects: string[];
}

interface UserPreferences {
  degree_program: string | null;
  current_semester: number | null;
  selected_courses: string[];
}

export const Study: React.FC = () => {
  const [session, setSession] = useState<StudySession>({
    currentCard: null,
    startTime: 0,
    sessionCards: [],
    completedCards: 0,
    totalCards: 0,
    selectedSubjects: [],
  });
  const [userAnswer, setUserAnswer] = useState('');
  const [showAnswer, setShowAnswer] = useState(false);
  const [answerSubmitted, setAnswerSubmitted] = useState(false);
  const [detailedExplanation, setDetailedExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [subjectDialogOpen, setSubjectDialogOpen] = useState(false);
  const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);

  useEffect(() => {
    // Load preferences
    fetchPreferences().catch(console.error);
  }, []);

  useEffect(() => {
    // Load subjects after preferences are loaded
    if (preferences) {
      fetchAvailableSubjects();
    }
  }, [preferences]);

  const fetchPreferences = async () => {
    try {
      const response = await axios.get('/api/preferences');
      setPreferences(response.data);
      // Auto-select all courses if available
      if (response.data.selected_courses && response.data.selected_courses.length > 0) {
        setSession(prev => ({
          ...prev,
          selectedSubjects: response.data.selected_courses,
        }));
        // Auto-start session if courses are selected
        if (response.data.selected_courses.length > 0) {
          setTimeout(() => startStudySession(), 100);
        }
      }
    } catch (error) {
      console.error('Failed to load preferences');
    }
  };

  const fetchAvailableSubjects = async () => {
    try {
      // Use preferences state (should be loaded by now)
      if (preferences?.selected_courses && preferences.selected_courses.length > 0) {
        setAvailableSubjects(preferences.selected_courses.sort());
        return;
      }
      
      // Fallback: Extract from flashcards
      const response = await axios.get('/api/flashcards/');
      const flashcards = response.data;
      
      // Extract unique subjects/courses from flashcards
      const subjects = new Set<string>();
      flashcards.forEach((card: Flashcard) => {
        // Try to get subject from tags (first tag is usually the course/subject)
        if (card.tags && card.tags.length > 0) {
          // Use the most relevant tag (usually the first one)
          const mainTag = card.tags.find(tag => 
            tag.includes('programming') || 
            tag.includes('data-structures') || 
            tag.includes('database') ||
            tag.includes('oop') ||
            tag.includes('algorithms') ||
            tag.includes('networks') ||
            tag.includes('ai') ||
            tag.includes('security')
          ) || card.tags[0];
          subjects.add(mainTag);
        }
        // Also check if there's a subject field
        if (card.subject) {
          subjects.add(card.subject);
        }
      });
      
      setAvailableSubjects(Array.from(subjects).sort());
    } catch (error) {
      console.error('Failed to load subjects');
    }
  };

  const startStudySession = async () => {
    if (session.selectedSubjects.length === 0) {
      toast.error('Please select at least one subject/course');
      setSubjectDialogOpen(true);
      return;
    }

    try {
      // Don't show loading state for better UX
      // Get all flashcards
      const response = await axios.get('/api/flashcards/');
      let cards = response.data;
      
      // Filter by selected subjects/courses
      cards = cards.filter((card: Flashcard) => {
        // Check if any tag matches selected subjects (case-insensitive)
        const hasMatchingTag = card.tags?.some(tag => 
          session.selectedSubjects.some(subject => {
            const tagLower = tag.toLowerCase();
            const subjectLower = subject.toLowerCase();
            
            // Direct match or contains
            if (tagLower === subjectLower || 
                tagLower.includes(subjectLower) || 
                subjectLower.includes(tagLower)) {
              return true;
            }
            
            // For course codes like CS1002, map to course-related keywords
            if (subject.match(/^[A-Z]{2}\d{4}$/)) {
              const courseMappings: { [key: string]: string[] } = {
                'CS1002': ['programming', 'basics', 'variables', 'functions'],
                'CS1004': ['oop', 'object-oriented', 'encapsulation', 'inheritance'],
                'CS2001': ['data-structures', 'arrays', 'trees', 'stack', 'queue'],
                'CS2005': ['database', 'sql', 'normalization', 'acid'],
                'CS2006': ['operating-systems', 'processes', 'threads', 'memory'],
                'CS2009': ['algorithms', 'complexity', 'big-o', 'sorting'],
                'CS3001': ['networks', 'tcp', 'udp', 'osi', 'dns'],
                'AI2002': ['ai', 'artificial-intelligence', 'machine-learning', 'neural'],
                'CS3002': ['security', 'cryptography', 'encryption', 'firewall'],
              };
              
              const keywords = courseMappings[subject] || [];
              return keywords.some(keyword => tagLower.includes(keyword));
            }
            
            return false;
          })
        );
        
        // Or check subject field
        const hasMatchingSubject = card.subject && 
          session.selectedSubjects.some(subject => {
            const cardSubjectLower = card.subject?.toLowerCase() || '';
            const subjectLower = subject.toLowerCase();
            return cardSubjectLower.includes(subjectLower) ||
                   subjectLower.includes(cardSubjectLower);
          });
        
        return hasMatchingTag || hasMatchingSubject;
      });
      
      if (cards.length === 0) {
        toast.error('No flashcards found for selected subjects');
        return;
      }

      // Shuffle cards for variety
      cards = cards.sort(() => Math.random() - 0.5);

      setSession(prev => ({
        ...prev,
        currentCard: cards[0],
        startTime: Date.now(),
        sessionCards: cards,
        completedCards: 0,
        totalCards: cards.length,
      }));
      
      toast.success(`Starting study session with ${cards.length} flashcards`);
    } catch (error) {
      toast.error('Failed to load study session');
    }
  };

  const calculateAccuracy = (userAnswer: string, correctAnswer: string): number => {
    const userLower = userAnswer.toLowerCase().trim();
    const correctLower = correctAnswer.toLowerCase().trim();
    
    // Exact match
    if (userLower === correctLower) {
      return 1.0;
    }
    
    // Check if user answer contains key words from correct answer
    const correctWords = correctLower.split(/\s+/).filter(w => w.length > 3);
    const matchingWords = correctWords.filter(word => userLower.includes(word));
    const wordMatchRatio = matchingWords.length / Math.max(correctWords.length, 1);
    
    // Check character similarity (simple Levenshtein-like)
    const maxLength = Math.max(userLower.length, correctLower.length);
    let matches = 0;
    const minLength = Math.min(userLower.length, correctLower.length);
    for (let i = 0; i < minLength; i++) {
      if (userLower[i] === correctLower[i]) matches++;
    }
    const charSimilarity = matches / maxLength;
    
    // Combine word matching and character similarity
    const accuracy = (wordMatchRatio * 0.6) + (charSimilarity * 0.4);
    
    // Ensure accuracy is between 0 and 1
    return Math.max(0, Math.min(1, accuracy));
  };

  const submitAnswer = async () => {
    if (!session.currentCard || !userAnswer.trim()) {
      toast.error('Please write your answer first');
      return;
    }

    setShowAnswer(true);
    setAnswerSubmitted(true);
    
    // Calculate accuracy based on answer comparison
    const accuracy = calculateAccuracy(userAnswer, session.currentCard.back);
    const responseTime = (Date.now() - session.startTime) / 1000;

    // Show feedback
    if (accuracy >= 0.8) {
      toast.success('Great answer! 🎉');
    } else if (accuracy >= 0.5) {
      toast('Good attempt! Keep practicing', { icon: '👍' });
    } else {
      toast('Review the correct answer carefully', { icon: '📚' });
    }

    // Submit to backend immediately (no delay)
    try {
      const response = await axios.post(`/api/flashcards/${session.currentCard!.id}/review`, {
        flashcard_id: session.currentCard!.id,
        response_accuracy: accuracy,
        response_time: responseTime,
        user_answer: userAnswer, // Send user's answer for detailed explanation
      });

      // Store detailed explanation if available
      if (response.data.detailed_explanation) {
        setDetailedExplanation(response.data.detailed_explanation);
      } else {
        setDetailedExplanation(null);
      }

      // Move to next card after 3 seconds (increased to allow reading explanation)
      setTimeout(() => {
        moveToNextCard();
      }, 3000);
    } catch (error) {
      toast.error('Failed to submit answer');
      setDetailedExplanation(null);
      // Still move to next card even if submission fails
      setTimeout(() => {
        moveToNextCard();
      }, 1500);
    }
  };

  const moveToNextCard = () => {
    const nextIndex = session.completedCards + 1;
    if (nextIndex < session.sessionCards.length) {
      setSession(prev => ({
        ...prev,
        currentCard: prev.sessionCards[nextIndex],
        completedCards: nextIndex,
        startTime: Date.now(),
      }));
      setUserAnswer('');
      setShowAnswer(false);
      setAnswerSubmitted(false);
      setDetailedExplanation(null);
    } else {
      // Session complete
      toast.success('Study session completed! Great job! 🎉');
      setSession(prev => ({
        ...prev,
        currentCard: null,
        completedCards: 0,
        totalCards: 0,
        sessionCards: [],
      }));
      setUserAnswer('');
      setShowAnswer(false);
      setAnswerSubmitted(false);
      setDetailedExplanation(null);
    }
  };

  const handleSubjectSelection = () => {
    if (session.selectedSubjects.length === 0) {
      toast.error('Please select at least one subject');
      return;
    }
    setSubjectDialogOpen(false);
    startStudySession();
  };

  // Removed loading state - show content immediately

  if (!session.currentCard && session.totalCards === 0) {
    return (
      <Box>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 2 }}>
            Study Session
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Select subjects/courses to start studying
          </Typography>
        </Box>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <School color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Select Subjects/Courses
              </Typography>
            </Box>

            {session.selectedSubjects.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Selected ({session.selectedSubjects.length}):
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {session.selectedSubjects.map((subject) => (
                    <Chip
                      key={subject}
                      label={subject}
                      onDelete={() => {
                        setSession(prev => ({
                          ...prev,
                          selectedSubjects: prev.selectedSubjects.filter(s => s !== subject),
                        }));
                      }}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}

            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={() => setSubjectDialogOpen(true)}
              size="large"
            >
              {session.selectedSubjects.length > 0 ? 'Change Subjects' : 'Select Subjects'}
            </Button>
          </CardContent>
        </Card>

        {/* Subject Selection Dialog */}
        <Dialog open={subjectDialogOpen} onClose={() => setSubjectDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Select Subjects/Courses to Study</DialogTitle>
          <DialogContent>
            <List>
              {availableSubjects.map((subject) => (
                <ListItem key={subject}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={session.selectedSubjects.includes(subject)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSession(prev => ({
                              ...prev,
                              selectedSubjects: [...prev.selectedSubjects, subject],
                            }));
                          } else {
                            setSession(prev => ({
                              ...prev,
                              selectedSubjects: prev.selectedSubjects.filter(s => s !== subject),
                            }));
                          }
                        }}
                      />
                    }
                    label={subject}
                  />
                </ListItem>
              ))}
            </List>
            {availableSubjects.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No subjects available. Add courses in the Flashcards page first.
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSubjectDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleSubjectSelection}
              variant="contained"
              disabled={session.selectedSubjects.length === 0}
            >
              Start Study Session
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  const progress = session.totalCards > 0 ? (session.completedCards / session.totalCards) * 100 : 0;

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 2 }}>
          Study Session
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2">
            {session.completedCards} / {session.totalCards}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={session.currentCard?.difficulty}
            color={session.currentCard?.difficulty === 'easy' ? 'success' : 
                   session.currentCard?.difficulty === 'medium' ? 'warning' : 'error'}
            size="small"
          />
          <Chip
            label={`${session.currentCard?.review_count || 0} reviews`}
            variant="outlined"
            size="small"
          />
          {session.currentCard?.tags && session.currentCard.tags.length > 0 && (
            <Chip
              label={session.currentCard.tags[0]}
              variant="outlined"
              size="small"
              color="primary"
            />
          )}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
        <motion.div
          style={{ width: '100%', maxWidth: 800 }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card sx={{ minHeight: 400 }}>
            <CardContent sx={{ p: 4 }}>
              {/* Question */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                  Question
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 'bold',
                    minHeight: 80,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {session.currentCard?.front}
                </Typography>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* User Answer Input */}
              {!showAnswer && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Write Your Answer
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your answer here..."
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />
                  <Button
                    variant="contained"
                    startIcon={<Send />}
                    onClick={submitAnswer}
                    disabled={!userAnswer.trim()}
                    size="large"
                    fullWidth
                  >
                    Submit Answer
                  </Button>
                </Box>
              )}

              {/* Show Answer */}
              {showAnswer && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                      Your Answer
                    </Typography>
                    <Card variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'action.hover' }}>
                      <Typography variant="body1">{userAnswer}</Typography>
                    </Card>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                      Correct Answer
                    </Typography>
                    <Card variant="outlined" sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {session.currentCard?.back}
                      </Typography>
                    </Card>
                  </Box>

                  {/* Detailed Explanation for Incorrect Answers */}
                  {detailedExplanation && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                        Detailed Explanation
                      </Typography>
                      <Card 
                        variant="outlined" 
                        sx={{ 
                          p: 2, 
                          bgcolor: 'rgba(25, 118, 210, 0.1)',
                          borderColor: 'primary.main',
                          borderWidth: 2,
                          borderStyle: 'solid'
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {detailedExplanation}
                        </Typography>
                      </Card>
                    </Box>
                  )}

                  {answerSubmitted && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      Progress updated! Moving to next card...
                    </Alert>
                  )}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Box>
  );
};
