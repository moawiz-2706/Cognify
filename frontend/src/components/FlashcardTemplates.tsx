import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Language,
  Science,
  Calculate,
  History,
  School,
  Quiz,
} from '@mui/icons-material';

interface Template {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  examples: string[];
  color: string;
}

const TEMPLATES: Template[] = [
  {
    id: 'language',
    name: 'Language Learning',
    description: 'Learn vocabulary, grammar, and phrases',
    icon: <Language />,
    color: '#4CAF50',
    examples: [
      'What does "hola" mean in Spanish?',
      'How do you say "thank you" in French?',
      'What is the past tense of "go"?',
    ],
  },
  {
    id: 'science',
    name: 'Science',
    description: 'Biology, chemistry, physics concepts',
    icon: <Science />,
    color: '#2196F3',
    examples: [
      'What is photosynthesis?',
      'What is the chemical formula for water?',
      'What is Newton\'s first law?',
    ],
  },
  {
    id: 'math',
    name: 'Mathematics',
    description: 'Formulas, equations, and problem-solving',
    icon: <Calculate />,
    color: '#FF9800',
    examples: [
      'What is the area of a circle?',
      'How do you solve 2x + 5 = 13?',
      'What is the Pythagorean theorem?',
    ],
  },
  {
    id: 'history',
    name: 'History',
    description: 'Historical events, dates, and figures',
    icon: <History />,
    color: '#9C27B0',
    examples: [
      'When did World War II end?',
      'Who was the first president of the USA?',
      'What was the Renaissance?',
    ],
  },
  {
    id: 'general',
    name: 'General Knowledge',
    description: 'Facts, trivia, and general information',
    icon: <School />,
    color: '#607D8B',
    examples: [
      'What is the capital of Japan?',
      'How many continents are there?',
      'What is the largest planet in our solar system?',
    ],
  },
];

interface FlashcardTemplatesProps {
  open: boolean;
  onClose: () => void;
  onSelectTemplate: (template: Template) => void;
}

export const FlashcardTemplates: React.FC<FlashcardTemplatesProps> = ({
  open,
  onClose,
  onSelectTemplate,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const handleSelect = () => {
    if (selectedTemplate) {
      onSelectTemplate(selectedTemplate);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Quiz color="primary" />
          Choose a Study Template
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Select a template to get started with pre-made examples and guidance for your subject.
        </Typography>
        
        <Grid container spacing={2}>
          {TEMPLATES.map((template) => (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: selectedTemplate?.id === template.id ? 2 : 1,
                  borderColor: selectedTemplate?.id === template.id ? template.color : 'divider',
                  '&:hover': {
                    boxShadow: 3,
                  },
                }}
                onClick={() => setSelectedTemplate(template)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Box sx={{ color: template.color }}>
                      {template.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {template.name}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" gutterBottom>
                      Example questions:
                    </Typography>
                    {template.examples.slice(0, 2).map((example, index) => (
                      <Typography
                        key={index}
                        variant="caption"
                        display="block"
                        sx={{ fontStyle: 'italic', color: 'text.secondary' }}
                      >
                        • {example}
                      </Typography>
                    ))}
                    {template.examples.length > 2 && (
                      <Typography variant="caption" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                        • And more...
                      </Typography>
                    )}
                  </Box>
                  
                  <Chip
                    label={`${template.examples.length} examples`}
                    size="small"
                    sx={{ backgroundColor: template.color, color: 'white' }}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSelect}
          variant="contained"
          disabled={!selectedTemplate}
        >
          Use This Template
        </Button>
      </DialogActions>
    </Dialog>
  );
};
