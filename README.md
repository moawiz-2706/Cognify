# Cognify - Adaptive Learning Assistant

An AI-powered flashcard system with adaptive learning capabilities using FastAPI, React, and intelligent scheduling algorithms.

## 🎯 What This App Does

Cognify is a smart flashcard application that uses adaptive learning algorithms to optimize your study sessions. It automatically adjusts the difficulty and scheduling of flashcards based on your performance, helping you learn more efficiently through spaced repetition and personalized recommendations.

## ✨ Key Features

### 🧠 **Adaptive Learning Engine**
- **SM-2 Algorithm**: Implements the proven SuperMemo 2 algorithm for optimal spaced repetition
- **Difficulty Adjustment**: Automatically adjusts card difficulty based on your performance
- **Smart Scheduling**: Cards are rescheduled based on how well you know them
- **Performance Tracking**: Tracks accuracy, response time, and learning progress

### 📚 **Smart Flashcard Management**
- **Easy Creation**: User-friendly interface for creating flashcards with templates
- **Subject Organization**: Organize cards by subject (Language, Science, Math, History, etc.)
- **Topic Tagging**: Add topics and tags for better organization
- **Template System**: Pre-built templates for common subjects
- **Bulk Operations**: Create multiple cards efficiently

### 📊 **Analytics Dashboard**
- **Learning Progress**: Visual charts showing your learning journey
- **Performance Metrics**: Track mastery rate, average difficulty, and study streaks
- **Due Cards**: See how many cards are due for review
- **Study Statistics**: Detailed analytics on your learning patterns

### 🎨 **Modern User Interface**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Material-UI Components**: Beautiful, accessible interface
- **Dark/Light Theme**: Comfortable viewing in any lighting
- **Intuitive Navigation**: Easy-to-use interface for all skill levels

### 🔄 **Study Sessions**
- **Interactive Reviews**: Engaging study sessions with immediate feedback
- **Performance Rating**: Rate your confidence level (1-5 stars)
- **Adaptive Timing**: Cards appear based on your learning schedule
- **Progress Tracking**: Real-time updates on your learning progress

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization
- **In-Memory Storage**: Simple, fast storage for development
- **Adaptive Learning**: SM-2 algorithm implementation
- **RESTful API**: Clean, well-documented API endpoints

### Frontend (React)
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Material-UI**: Beautiful component library
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cognify
   ```

2. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip install -r requirements-simple.txt
   
   # Run the backend
   python3 simple_run.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

   For production or Vercel deployments, set the API host first:
   ```bash
   REACT_APP_API_BASE_URL=https://your-backend-domain.com
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - API Documentation: http://localhost:3001/docs

## 🌐 Deployment

### What to deploy where
- The frontend is a React single-page app and is ready for Vercel.
- The backend is a FastAPI service and should be deployed separately on a Python-friendly host such as Render, Railway, Fly.io, or a VPS.
- The frontend reads its backend URL from `REACT_APP_API_BASE_URL`, so the same build can run locally and in production.

### Deploy the frontend to Vercel
1. Push this repository to GitHub.
2. Create a new Vercel project from that GitHub repository.
3. Set the **Root Directory** to `frontend`.
4. Use the default build settings or set them explicitly to:
   - Build Command: `npm run build`
   - Output Directory: `build`
5. Add an environment variable in Vercel:
   - `REACT_APP_API_BASE_URL=https://your-backend-domain.com`
6. Deploy. The Vercel config in `frontend/vercel.json` keeps React Router refreshes working.

### Push to GitHub
If the project is not already initialized as a git repository locally, run:
```bash
git init
git add .
git commit -m "Initial Cognify deployment setup"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Frontend environment example
- Copy `frontend/.env.example` to `frontend/.env.local` for local production-style testing.
- Set `REACT_APP_API_BASE_URL=http://localhost:3001` for local backend access.

## 📖 Complete Workflow

### Step 1: Getting Started
1. **Open the app** at `http://localhost:3000`
2. **Navigate to Dashboard** to see your learning overview
3. **View analytics** showing total cards, due cards, and mastery rate

### Step 2: Creating Flashcards
1. **Go to Flashcards page**
2. **Click "Create New Card"** or **"Use Template"**
3. **Fill in the form**:
   - **Subject**: Choose from Language, Science, Math, History, etc.
   - **Topic**: Optional topic (e.g., "World Capitals", "Algebra")
   - **Question**: The front of your flashcard
   - **Answer**: The back of your flashcard
   - **Difficulty**: Easy, Medium, or Hard
   - **Tags**: Optional tags for organization
4. **Click "Create Card"** to save

### Step 3: Using Templates
1. **Click "Use Template"** for quick setup
2. **Choose a template**:
   - **Language Learning**: Vocabulary and grammar
   - **Science**: Concepts and definitions
   - **Mathematics**: Formulas and equations
   - **History**: Events and dates
   - **General Knowledge**: Facts and trivia
3. **Template pre-fills** the form with examples
4. **Customize** the content as needed

### Step 4: Studying
1. **Go to Study page**
2. **Click "Start Study Session"**
3. **Review cards** that are due:
   - **Read the question**
   - **Think of the answer**
   - **Click "Show Answer"**
   - **Rate your performance** (1-5 stars)
4. **Get feedback** and recommendations
5. **Continue** until all due cards are reviewed

### Step 5: Tracking Progress
1. **Visit Analytics page**
2. **View your statistics**:
   - Total cards created
   - Cards due for review
   - New cards to learn
   - Mastered cards
   - Average difficulty
   - Mastery rate percentage
3. **Monitor your learning journey**

### Step 6: Managing Cards
1. **Go to Flashcards page**
2. **View all your cards** in a grid layout
3. **Edit cards** by clicking the options menu
4. **Delete cards** you no longer need
5. **Filter and search** through your collection

## 🔧 API Endpoints

### Flashcard Management
- `GET /api/flashcards/` - Get all flashcards
- `POST /api/flashcards/` - Create a new flashcard
- `GET /api/flashcards/{id}` - Get specific flashcard
- `PUT /api/flashcards/{id}` - Update flashcard
- `DELETE /api/flashcards/{id}` - Delete flashcard

### Study System
- `GET /api/flashcards/due` - Get flashcards due for review
- `POST /api/flashcards/{id}/review` - Submit review session

### Analytics
- `GET /api/analytics/learning` - Get learning analytics

## 🧮 Adaptive Learning Algorithm

### SM-2 Algorithm Implementation
The app uses the SuperMemo 2 algorithm for optimal spaced repetition:

1. **Initial Learning**: New cards start with 1-day interval
2. **Performance Rating**: Rate your confidence (1-5 stars)
3. **Interval Calculation**: 
   - Correct answers increase the interval
   - Incorrect answers reset to 1 day
   - Easy answers get longer intervals
4. **Difficulty Adjustment**: Cards become easier or harder based on performance
5. **Smart Scheduling**: Due cards appear at optimal times for retention

### Performance Metrics
- **Accuracy Rate**: Percentage of correct answers
- **Response Time**: How quickly you answer
- **Mastery Level**: How well you know each card
- **Learning Curve**: Your progress over time

## 🎨 User Interface Features

### Dashboard
- **Overview Cards**: Quick stats at a glance
- **Progress Charts**: Visual representation of learning
- **Recent Activity**: Latest study sessions
- **Quick Actions**: Fast access to common tasks

### Flashcard Creator
- **Live Preview**: See your card as you type
- **Template System**: Pre-built examples for common subjects
- **Validation**: Real-time form validation
- **Auto-save**: Never lose your work

### Study Interface
- **Clean Design**: Distraction-free study environment
- **Progress Indicator**: See how many cards remain
- **Performance Rating**: Easy 1-5 star rating system
- **Immediate Feedback**: Instant results and recommendations

### Analytics Dashboard
- **Visual Charts**: Easy-to-understand graphs
- **Key Metrics**: Important learning statistics
- **Trend Analysis**: Track progress over time
- **Performance Insights**: Understand your learning patterns

## 🔄 Data Flow

1. **User creates flashcard** → Stored in backend with metadata
2. **User starts study session** → System fetches due cards
3. **User reviews card** → Performance data collected
4. **User rates performance** → Algorithm calculates next review time
5. **System updates card** → New difficulty and schedule set
6. **Analytics updated** → Progress tracked and displayed

## 🛠️ Development

### Running in Development
```bash
# Backend (Terminal 1)
python3 simple_run.py

# Frontend (Terminal 2)
cd frontend
npm start
```

### Code Structure
```
├── app/
│   ├── simple_main.py          # FastAPI application
│   ├── simple_models.py        # Pydantic models
│   ├── simple_service.py       # Business logic
│   └── simple_routes.py       # API routes
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   └── App.tsx            # Main app component
│   └── package.json
└── README.md
```

## 🎯 Use Cases

### Students
- **Exam Preparation**: Create cards for any subject
- **Language Learning**: Vocabulary and grammar practice
- **Science Study**: Memorize formulas and concepts
- **History Review**: Remember dates and events

### Professionals
- **Certification Prep**: Study for professional exams
- **Skill Development**: Learn new technologies
- **Presentation Prep**: Memorize key points
- **Training Materials**: Create learning content

### Educators
- **Class Preparation**: Create study materials
- **Student Assessment**: Track learning progress
- **Content Creation**: Build educational resources
- **Performance Analysis**: Understand learning patterns

## 🚀 Future Enhancements

- **Mobile App**: Native iOS and Android apps
- **Offline Support**: Study without internet connection
- **Collaborative Learning**: Share cards with others
- **Advanced Analytics**: More detailed learning insights
- **Voice Recognition**: Speak your answers
- **Multi-language Support**: Learn in different languages
- **AI Recommendations**: Personalized study suggestions
- **Gamification**: Points, badges, and achievements

## 📞 Support

For questions and support:
- Check the API documentation at `/docs`
- Review the code comments
- Create an issue on GitHub

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Start your adaptive learning journey today!** 🚀