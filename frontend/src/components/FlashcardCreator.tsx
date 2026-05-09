import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  Autocomplete,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { School } from '@mui/icons-material';
import axios from '../lib/api';
import toast from 'react-hot-toast';

interface FlashcardForm {
  subject: string;
  topic: string;
  question: string;
  answer: string;
  difficulty: string;
  tags: string[];
}

interface Course {
  code: string;
  name: string;
  credit_hours: string;
  semester: number;
}

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: 'Easy', description: 'Basic concepts, simple facts' },
  { value: 'medium', label: 'Medium', description: 'Moderate understanding required' },
  { value: 'hard', label: 'Hard', description: 'Advanced concepts, complex topics' },
];

const COMMON_TAGS = [
  'vocabulary', 'grammar', 'formulas', 'definitions', 'dates', 'facts',
  'concepts', 'theories', 'examples', 'practice', 'review', 'exam'
];

interface FlashcardCreatorProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  editingCard?: any;
}

export const FlashcardCreator: React.FC<FlashcardCreatorProps> = ({
  open,
  onClose,
  onSubmit,
  editingCard
}) => {
  const [selectedDifficulty, setSelectedDifficulty] = useState(editingCard?.difficulty || 'medium');
  const [availableCourses, setAvailableCourses] = useState<Course[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);

  useEffect(() => {
    if (open) {
      fetchUserCourses();
    }
  }, [open]);

  const fetchUserCourses = async () => {
    try {
      setLoadingCourses(true);
      // Get user preferences to find selected courses
      const prefsResponse = await axios.get('/api/preferences');
      const selectedCourseCodes = prefsResponse.data.selected_courses || [];
      
      if (selectedCourseCodes.length === 0) {
        setAvailableCourses([]);
        setLoadingCourses(false);
        return;
      }

      // Get full curriculum to get course names
      const curriculumResponse = await axios.get('/api/curriculum');
      const curriculum = curriculumResponse.data;
      
      // Extract courses from all semesters
      const allCourses: Course[] = [];
      Object.values(curriculum).forEach((semester: any) => {
        if (semester.courses) {
          allCourses.push(...semester.courses);
        }
      });

      // Filter to only selected courses
      const userCourses = allCourses.filter(course => 
        selectedCourseCodes.includes(course.code)
      );

      setAvailableCourses(userCourses);
    } catch (error) {
      console.error('Failed to load courses:', error);
      setAvailableCourses([]);
    } finally {
      setLoadingCourses(false);
    }
  };
  
  const { control, handleSubmit, reset, watch } = useForm<FlashcardForm>({
    defaultValues: {
      subject: editingCard?.subject || '',
      topic: editingCard?.topic || '',
      question: editingCard?.front || '',
      answer: editingCard?.back || '',
      difficulty: editingCard?.difficulty || 'medium',
      tags: editingCard?.tags || [],
    },
  });

  // Reset form when editingCard changes (after useForm declaration)
  useEffect(() => {
    if (open) {
      reset({
        subject: editingCard?.subject || '',
        topic: editingCard?.topic || '',
        question: editingCard?.front || '',
        answer: editingCard?.back || '',
        difficulty: editingCard?.difficulty || 'medium',
        tags: editingCard?.tags || [],
      });
      setSelectedDifficulty(editingCard?.difficulty || 'medium');
    }
  }, [open, editingCard, reset]);

  const watchedValues = watch();

  const handleFormSubmit = (data: FlashcardForm) => {
    console.log('Form submitted with data:', data);
    
    // Validate required fields with detailed checks
    const question = data.question?.trim() || '';
    const answer = data.answer?.trim() || '';
    const subject = data.subject?.trim() || '';

    if (!question || question.length === 0) {
      toast.error('Question is required');
      return;
    }
    if (!answer || answer.length === 0) {
      toast.error('Answer is required');
      return;
    }
    if (!subject || subject.length === 0) {
      toast.error('Subject is required. Please select a course.');
      return;
    }

    const flashcardData = {
      question: question,
      answer: answer,
      tags: data.tags || [],
      difficulty: data.difficulty || 'medium',
      subject: subject,
      topic: data.topic?.trim() || null,
    };

    console.log('Sending flashcard data:', flashcardData);
    
    // Final validation before calling onSubmit
    if (!flashcardData.question || !flashcardData.answer || !flashcardData.subject) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    onSubmit(flashcardData);
    reset();
    onClose();
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const getSubjectIcon = (subject: string) => {
    return <School />;
  };

  const getDifficultyDescription = (difficulty: string) => {
    const option = DIFFICULTY_OPTIONS.find(opt => opt.value === difficulty);
    return option?.description || '';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <School color="primary" />
          {editingCard ? 'Edit Flashcard' : 'Create New Flashcard'}
        </Box>
      </DialogTitle>
      
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogContent>
          <Grid container spacing={3}>
            {/* Subject Selection */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Subject</InputLabel>
                <Controller
                  name="subject"
                  control={control}
                  rules={{ 
                    required: 'Please select a subject',
                    validate: (value) => (value && value.trim().length > 0) || 'Subject is required'
                  }}
                  render={({ field, fieldState }) => (
                    <Select
                      {...field}
                      label="Subject"
                      error={!!fieldState.error}
                      disabled={loadingCourses || availableCourses.length === 0}
                      value={field.value || ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        field.onChange(value);
                      }}
                    >
                      {availableCourses.length === 0 ? (
                        <MenuItem disabled>
                          <Typography variant="body2" color="text.secondary">
                            {loadingCourses ? 'Loading courses...' : 'No courses selected. Please add courses in the Flashcards page.'}
                          </Typography>
                        </MenuItem>
                      ) : (
                        availableCourses.map((course) => (
                          <MenuItem key={course.code} value={course.code}>
                            <Box>
                              <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                                {course.code}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {course.name}
                              </Typography>
                            </Box>
                          </MenuItem>
                        ))
                      )}
                    </Select>
                  )}
                />
                {availableCourses.length === 0 && !loadingCourses && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                    Please select courses in the Academic Setup section above
                  </Typography>
                )}
              </FormControl>
            </Grid>

            {/* Topic */}
            <Grid item xs={12} md={6}>
              <Controller
                name="topic"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Topic (optional)"
                    fullWidth
                    placeholder="e.g., Chapter 5, Unit 3, Basic Algebra"
                    helperText="What specific topic or chapter is this about?"
                  />
                )}
              />
            </Grid>

            {/* Question */}
            <Grid item xs={12}>
              <Controller
                name="question"
                control={control}
                rules={{ 
                  required: 'Question is required',
                  validate: (value) => (value && value.trim().length > 0) || 'Question cannot be empty'
                }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Question"
                    fullWidth
                    multiline
                    rows={3}
                    error={!!fieldState.error}
                    helperText={fieldState.error?.message || "What do you want to learn or remember?"}
                    placeholder="e.g., What is the capital of France? How do you solve quadratic equations?"
                    value={field.value || ''}
                    onChange={(e) => field.onChange(e.target.value)}
                  />
                )}
              />
            </Grid>

            {/* Answer */}
            <Grid item xs={12}>
              <Controller
                name="answer"
                control={control}
                rules={{ 
                  required: 'Answer is required',
                  validate: (value) => ((value && value.trim().length > 0)) || 'Answer cannot be empty'
                }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Answer"
                    fullWidth
                    multiline
                    rows={3}
                    error={!!fieldState.error}
                    helperText={fieldState.error?.message || "The correct answer or explanation"}
                    placeholder="e.g., Paris. The capital of France is Paris, located in northern France."
                    value={field.value || ''}
                    onChange={(e) => field.onChange(e.target.value)}
                  />
                )}
              />
            </Grid>

            {/* Difficulty */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Controller
                  name="difficulty"
                  control={control}
                  render={({ field }) => (
                    <Select
                      {...field}
                      label="Difficulty Level"
                      onChange={(e) => {
                        field.onChange(e);
                        setSelectedDifficulty(e.target.value);
                      }}
                    >
                      {DIFFICULTY_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <Box>
                            <Typography variant="body1">{option.label}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {option.description}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  )}
                />
                {selectedDifficulty && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                    {getDifficultyDescription(selectedDifficulty)}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            {/* Tags */}
            <Grid item xs={12} md={6}>
              <Controller
                name="tags"
                control={control}
                render={({ field }) => (
                  <Autocomplete
                    {...field}
                    multiple
                    freeSolo
                    options={COMMON_TAGS}
                    value={field.value || []}
                    onChange={(_, newValue) => field.onChange(newValue)}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                        />
                      ))
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Tags (optional)"
                        placeholder="Add tags to organize your cards"
                        helperText="e.g., vocabulary, exam, review, practice"
                      />
                    )}
                  />
                )}
              />
            </Grid>

            {/* Preview */}
            {watchedValues.question && watchedValues.answer && (
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Preview
                </Typography>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      {getSubjectIcon(watchedValues.subject)}
                      <Typography variant="subtitle1" fontWeight="bold">
                        {availableCourses.find(c => c.code === watchedValues.subject)?.code || watchedValues.subject}
                      </Typography>
                      {watchedValues.topic && (
                        <>
                          <Typography variant="body2" color="text.secondary">•</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {watchedValues.topic}
                          </Typography>
                        </>
                      )}
                    </Box>
                    {watchedValues.subject && (
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                        {availableCourses.find(c => c.code === watchedValues.subject)?.name}
                      </Typography>
                    )}
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Question:
                      </Typography>
                      <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                        {watchedValues.question}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Answer:
                      </Typography>
                      <Typography variant="body1">
                        {watchedValues.answer}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={watchedValues.difficulty}
                        color={watchedValues.difficulty === 'easy' ? 'success' : 
                               watchedValues.difficulty === 'medium' ? 'warning' : 'error'}
                        size="small"
                      />
                      {watchedValues.tags?.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {editingCard ? 'Update Flashcard' : 'Create Flashcard'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
