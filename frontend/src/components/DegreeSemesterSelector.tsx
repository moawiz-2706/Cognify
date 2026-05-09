import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
} from '@mui/material';
import {
  Add,
  School,
} from '@mui/icons-material';
import axios from '../lib/api';
import toast from 'react-hot-toast';

interface Course {
  code: string;
  name: string;
  credit_hours: string;
  semester: number;
}

interface UserPreferences {
  degree_program: string | null;
  current_semester: number | null;
  selected_courses: string[];
}

export const DegreeSemesterSelector: React.FC = () => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    degree_program: null,
    current_semester: null,
    selected_courses: [],
  });
  const [semesterCourses, setSemesterCourses] = useState<Course[]>([]);
  const [courseDialogOpen, setCourseDialogOpen] = useState(false);
  const [selectedCoursesToAdd, setSelectedCoursesToAdd] = useState<string[]>([]);

  useEffect(() => {
    fetchPreferences();
  }, []);

  useEffect(() => {
    if (preferences.current_semester) {
      fetchSemesterCourses(preferences.current_semester);
    }
  }, [preferences.current_semester]);

  const fetchPreferences = async () => {
    try {
      const response = await axios.get('/api/preferences');
      setPreferences(response.data);
    } catch (error) {
      console.error('Failed to load preferences');
    }
  };

  const fetchSemesterCourses = async (semester: number) => {
    try {
      const response = await axios.get(`/api/curriculum/semester/${semester}`);
      setSemesterCourses(response.data);
    } catch (error) {
      toast.error('Failed to load semester courses');
    }
  };

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    try {
      const response = await axios.put('/api/preferences', updates);
      setPreferences(response.data);
      toast.success('Preferences updated');
      
      // If semester changed, reload courses
      if (updates.current_semester !== undefined) {
        fetchSemesterCourses(updates.current_semester!);
      }
    } catch (error) {
      toast.error('Failed to update preferences');
    }
  };

  const handleRemoveCourse = async (courseCode: string) => {
    try {
      await axios.delete(`/api/preferences/courses/${courseCode}`);
      await fetchPreferences();
      toast.success(`Course ${courseCode} removed`);
    } catch (error) {
      toast.error('Failed to remove course');
    }
  };

  const handleOpenCourseDialog = () => {
    setSelectedCoursesToAdd([]);
    setCourseDialogOpen(true);
  };

  const handleAddMultipleCourses = async () => {
    try {
      const results = [];
      for (const courseCode of selectedCoursesToAdd) {
        try {
          const response = await axios.post(`/api/preferences/courses/${courseCode}`, {}, {
            withCredentials: true
          });
          results.push({ 
            courseCode, 
            success: true, 
            message: response.data?.message,
            flashcardsGenerated: response.data?.flashcards_generated || 0
          });
        } catch (error: any) {
          let errorMsg = 'Failed to add';
          if (error.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
              errorMsg = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
            } else if (typeof detail === 'string') {
              errorMsg = detail;
            }
          }
          results.push({ 
            courseCode, 
            success: false, 
            message: errorMsg
          });
        }
      }
      
      const successCount = results.filter(r => r.success).length;
      const failedCount = results.filter(r => !r.success).length;
      const totalFlashcards = results
        .filter(r => r.success && r.flashcardsGenerated)
        .reduce((sum, r) => sum + (r.flashcardsGenerated || 0), 0);
      
      await fetchPreferences();
      
      if (failedCount === 0) {
        if (totalFlashcards > 0) {
          toast.success(`Successfully added ${successCount} course(s) with ${totalFlashcards} flashcards`);
        } else {
          toast.success(`Successfully added ${successCount} course(s). Generating flashcards...`);
        }
      } else {
        toast.error(`Added ${successCount} course(s), ${failedCount} failed`);
        // Show details of failed courses
        results.filter(r => !r.success).forEach(r => {
          toast.error(`${r.courseCode}: ${r.message}`, { duration: 3000 });
        });
      }
      
      setCourseDialogOpen(false);
      setSelectedCoursesToAdd([]);
      
      // Trigger flashcard refresh event
      window.dispatchEvent(new CustomEvent('flashcardsUpdated'));
      
      // Reload page to show new flashcards after a short delay
      if (successCount > 0) {
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (error: any) {
      console.error('Error adding multiple courses:', error);
      let errorMessage = 'Failed to add courses';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <School color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Academic Setup
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Degree Program</InputLabel>
              <Select
                value={preferences.degree_program || ''}
                label="Degree Program"
                onChange={(e) => updatePreferences({ degree_program: e.target.value })}
              >
                <MenuItem value="CS">Computer Science (CS)</MenuItem>
                <MenuItem value="SE">Software Engineering (SE)</MenuItem>
                <MenuItem value="AI">Artificial Intelligence (AI)</MenuItem>
                <MenuItem value="DS">Data Science (DS)</MenuItem>
                <MenuItem value="CYS">Cybersecurity (CYS)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Current Semester</InputLabel>
              <Select
                value={preferences.current_semester || ''}
                label="Current Semester"
                onChange={(e) => updatePreferences({ current_semester: Number(e.target.value) })}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
                  <MenuItem key={sem} value={sem}>
                    Semester {sem}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<Add />}
              onClick={handleOpenCourseDialog}
              disabled={!preferences.current_semester}
            >
              Add Courses
            </Button>
          </Grid>
        </Grid>

        {preferences.selected_courses.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
              Selected Courses ({preferences.selected_courses.length}):
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {preferences.selected_courses.map((courseCode) => {
                const course = semesterCourses.find(c => c.code === courseCode);
                return (
                  <Chip
                    key={courseCode}
                    label={course ? `${courseCode} - ${course.name}` : courseCode}
                    onDelete={() => handleRemoveCourse(courseCode)}
                    color="primary"
                    variant="outlined"
                  />
                );
              })}
            </Box>
          </Box>
        )}

        {preferences.current_semester && semesterCourses.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {semesterCourses.length} courses available for Semester {preferences.current_semester}
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* Course Selection Dialog */}
      <Dialog open={courseDialogOpen} onClose={() => setCourseDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Select Courses for Semester {preferences.current_semester}</DialogTitle>
        <DialogContent>
          <List>
            {semesterCourses
              .filter(c => !preferences.selected_courses.includes(c.code))
              .map((course) => (
                <ListItem key={course.code}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={selectedCoursesToAdd.includes(course.code)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCoursesToAdd([...selectedCoursesToAdd, course.code]);
                          } else {
                            setSelectedCoursesToAdd(selectedCoursesToAdd.filter(c => c !== course.code));
                          }
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {course.code}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {course.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {course.credit_hours} credit hours
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCourseDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAddMultipleCourses}
            variant="contained"
            disabled={selectedCoursesToAdd.length === 0}
          >
            Add {selectedCoursesToAdd.length} Course(s)
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

