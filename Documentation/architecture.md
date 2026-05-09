# Cognify Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Architecture](#data-architecture)
5. [Agent Architecture](#agent-architecture)
6. [API Architecture](#api-architecture)
7. [Database Schema](#database-schema)
8. [Memory Architecture](#memory-architecture)
9. [Integration Architecture](#integration-architecture)
10. [Technology Stack](#technology-stack)
11. [Data Flow](#data-flow)
12. [Deployment Architecture](#deployment-architecture)

---

## System Overview

Cognify is an adaptive learning assistant that uses AI-powered algorithms to optimize flashcard-based learning through spaced repetition, difficulty adjustment, and personalized recommendations.

### Key Features
- *Adaptive Learning*: Automatically adjusts flashcard difficulty based on performance
- *Spaced Repetition*: Optimizes review scheduling using performance-based algorithms
- *Learning Analytics*: Tracks progress, accuracy, and mastery levels
- *Multi-Agent Integration*: Can integrate with supervisor systems

---

## High-Level Architecture


┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  (React + Material-UI)                                      │
│  - Dashboard, Flashcards, Study, Analytics                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│                      API Layer                               │
│  (FastAPI)                                                   │
│  - Authentication Router                                      │
│  - Flashcard Router                                          │
│  - CORS Middleware                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Service Layer                            │
│  - FlashcardService                                         │
│  - AuthService                                              │
│  - AnalyticsService                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐         ┌─────────▼──────────┐
│ Cognify Agent  │         │   Database Layer   │
│ (LangGraph)    │         │  (SQLAlchemy ORM)  │
│                │         │                    │
│ - Performance  │         │ - Users            │
│   Analysis     │         │ - Flashcards       │
│ - Scheduling   │         │ - Review Sessions  │
│ - Recommendations         │                    │
└────────────────┘         └────────────────────┘


---

## Component Architecture

### 1. Frontend Layer
*Location*: frontend/

*Components*:
- *Dashboard* (pages/Dashboard.tsx): Overview of learning progress
- *Flashcards* (pages/Flashcards.tsx): Flashcard management interface
- *Study* (pages/Study.tsx): Interactive study sessions
- *Analytics* (pages/Analytics.tsx): Learning analytics and charts
- *FlashcardCreator* (components/FlashcardCreator.tsx): Create/edit flashcards
- *DegreeSemesterSelector* (components/DegreeSemesterSelector.tsx): Course selection

*Technology*: React, TypeScript, Material-UI, Axios

### 2. API Layer
*Location*: app/main.py, app/routers/

*Components*:
- *Main Application* (app/main.py): FastAPI app initialization
- *Auth Router* (app/routers/auth.py): Authentication endpoints
- *Flashcard Router* (app/routers/flashcards.py): Flashcard CRUD and review endpoints

*Endpoints*:

POST   /auth/register      - User registration
POST   /auth/login         - User login
GET    /flashcards/        - Get all flashcards
POST   /flashcards/        - Create flashcard
GET    /flashcards/due     - Get due flashcards
POST   /flashcards/{id}/review - Submit review
GET    /flashcards/analytics/learning - Get analytics


### 3. Service Layer
*Location*: app/services/

*Components*:
- *FlashcardService* (app/services/flashcard_service.py):
  - CRUD operations for flashcards
  - Review processing with Cognify agent
  - Due flashcards retrieval
  - Learning analytics calculation

- *AuthService* (app/services/auth.py):
  - User authentication
  - JWT token generation/validation
  - Password hashing

- *AnalyticsService* (app/services/analytics_service.py):
  - Learning analytics aggregation
  - Performance trend analysis

### 4. Agent Layer
*Location*: app/agents/cognify_agent.py

*Components*:
- *CognifyAgent*: Main adaptive learning agent
- *LangGraph Workflow*: Stateful processing pipeline
- *AgentState*: TypedDict for state management

*Workflow Nodes*:
1. analyze_performance: Calculates performance metrics
2. update_schedule: Determines next review time (spaced repetition)
3. generate_recommendation: Creates personalized recommendations
4. share_learning_data: Placeholder for supervisor integration

### 5. Database Layer
*Location*: app/database.py

*Components*:
- *SQLAlchemy ORM*: Database abstraction
- *Models*: User, Flashcard, ReviewSession
- *Session Management*: Database connection pooling

---

## Data Architecture

### Data Flow


User Action
    ↓
Frontend (React)
    ↓
HTTP Request (REST API)
    ↓
FastAPI Router
    ↓
Service Layer
    ↓
┌─────────────┬──────────────┐
│   Agent     │   Database   │
│ (Processing)│ (Persistence)│
└─────────────┴──────────────┘
    ↓              ↓
Response ←─────────┘
    ↓
Frontend Update


### State Management

*Ephemeral State* (AgentState):
- Exists only during review processing
- Managed by LangGraph workflow
- Contains: performance metrics, difficulty scores, recommendations

*Persistent State* (Database):
- User accounts
- Flashcard content and learning state
- Complete review history
- Analytics data

---

## Agent Architecture

### LangGraph Workflow


┌─────────────────────────────────────────────────┐
│            Cognify Agent Workflow               │
└─────────────────────────────────────────────────┘

Entry Point
    ↓
┌─────────────────────┐
│ analyze_performance │
│                     │
│ - Calculate time    │
│   score             │
│ - Calculate         │
│   accuracy score    │
│ - Weighted          │
│   performance       │
│ - Update difficulty │
│   score             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   update_schedule   │
│                     │
│ - Calculate         │
│   performance       │
│   score             │
│ - Determine review  │
│   interval          │
│ - Set next_review   │
│   _time             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│generate_recommendation│
│                     │
│ - Analyze           │
│   performance       │
│ - Generate          │
│   personalized      │
│   feedback          │
│ - Add time-based    │
│   suggestions       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ share_learning_data │
│                     │
│ - Prepare data      │
│   for supervisor    │
│ - Log learning      │
│   metrics           │
└──────────┬──────────┘
           │
           ▼
         END


### AgentState Structure

python
class AgentState(TypedDict):
    user_id: str                    # User identifier
    flashcard_id: str               # Flashcard identifier
    response_accuracy: float        # 0.0-1.0 accuracy score
    response_time: float            # Response time in seconds
    current_difficulty: float       # Current difficulty (0.0-1.0)
    review_count: int               # Total reviews
    correct_count: int              # Correct answers
    next_review_time: datetime      # Scheduled review time
    difficulty_score: float         # Calculated difficulty
    recommendation: str             # Personalized feedback
    performance_analysis: Dict      # Detailed metrics


### Algorithm Details

#### 1. Performance Analysis
python
time_score = calculate_time_score(response_time)
accuracy_score = response_accuracy
performance_score = (accuracy_score * 0.7) + (time_score * 0.3)

if performance_score >= 0.8:
    difficulty_score += 0.1  # Increase difficulty
elif performance_score <= 0.4:
    difficulty_score -= 0.1  # Decrease difficulty


#### 2. Spaced Repetition Scheduling
python
if performance_score >= 0.8:
    # Good performance - increase interval
    interval = 24 * (2.0 + difficulty * 0.5)  # 48-60 hours
elif performance_score >= 0.6:
    # Moderate - maintain interval
    interval = 24  # 24 hours
else:
    # Poor performance - decrease interval
    interval = 6 / (1 + difficulty)  # 3-6 hours


#### 3. Difficulty Level Conversion
python
if difficulty_score <= 0.33:
    difficulty = EASY
elif difficulty_score <= 0.66:
    difficulty = MEDIUM
else:
    difficulty = HARD


---

## API Architecture

### REST API Structure


/api
├── /auth
│   ├── POST /register      - Register new user
│   └── POST /login         - Authenticate user
│
└── /flashcards
    ├── GET    /            - List all flashcards
    ├── POST   /            - Create flashcard
    ├── GET    /{id}        - Get specific flashcard
    ├── PUT    /{id}        - Update flashcard
    ├── DELETE /{id}        - Delete flashcard
    ├── GET    /due         - Get due flashcards
    ├── POST   /{id}/review - Submit review session
    └── GET    /analytics/learning - Get analytics


### Request/Response Flow


Client Request
    ↓
FastAPI Router (with auth dependency)
    ↓
Service Layer (business logic)
    ↓
┌─────────────┬──────────────┐
│   Agent     │   Database   │
│ (if review) │ (CRUD ops)   │
└─────────────┴──────────────┘
    ↓
Service Response
    ↓
Router Response (Pydantic model)
    ↓
Client


### Authentication Flow


1. User Registration/Login
   ↓
2. JWT Token Generation
   ↓
3. Token in Authorization Header
   ↓
4. Token Validation (get_current_user dependency)
   ↓
5. Authenticated Request Processing


---

## Database Schema

### Entity Relationship Diagram


┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
│ is_active   │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐
│     Flashcard       │
├─────────────────────┤
│ id (PK)             │
│ front               │
│ back                │
│ tags                │
│ difficulty          │
│ status              │
│ difficulty_score    │
│ next_review_time    │
│ review_count        │
│ correct_count       │
│ user_id (FK)        │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐
│   ReviewSession     │
├─────────────────────┤
│ id (PK)             │
│ flashcard_id (FK)   │
│ user_id (FK)        │
│ response_accuracy   │
│ response_time       │
│ created_at          │
└─────────────────────┘


### Table Details

#### Users Table
- *Purpose*: User accounts and authentication
- *Key Fields*: id, username, email, hashed_password
- *Relationships*: One-to-many with Flashcards and ReviewSessions

#### Flashcards Table
- *Purpose*: Flashcard content and learning state
- *Key Fields*: 
  - Content: front, back, tags
  - Learning State: difficulty, difficulty_score, status
  - Scheduling: next_review_time
  - Progress: review_count, correct_count
- *Relationships*: Many-to-one with User, One-to-many with ReviewSessions

#### ReviewSessions Table
- *Purpose*: Complete review history
- *Key Fields*: response_accuracy, response_time, created_at
- *Relationships*: Many-to-one with Flashcard and User

---

## Memory Architecture

### Memory Types in Cognify

#### 1. Ephemeral Memory (AgentState)
- *Type*: In-memory TypedDict
- *Duration*: Single review processing session
- *Purpose*: State management during LangGraph workflow
- *Lifecycle*: Created → Processed → Discarded

#### 2. Persistent Memory (Database)
- *Type*: SQL Database (SQLite/PostgreSQL)
- *Duration*: Permanent
- *Purpose*: Long-term storage of learning data
- *Tables*: Users, Flashcards, ReviewSessions

### Memory Flow


Review Request
    ↓
Load Flashcard from Database (persistent)
    ↓
Create AgentState (ephemeral)
    ↓
Process through LangGraph workflow
    ↓
Update Flashcard in Database (persistent)
    ↓
Save ReviewSession to Database (persistent)
    ↓
Discard AgentState (ephemeral)


### No Caching System
- Cognify does NOT use STM (Short-Term Memory)
- Cognify does NOT use LTM (Long-Term Memory cache)
- Each review is processed independently
- All state is loaded from database each time

---

## Integration Architecture

### Multi-Agent System Integration


┌─────────────────────────────────────────┐
│         Supervisor System               │
│  - Routes requests                      │
│  - Manages agent registry               │
└──────────────┬──────────────────────────┘
               │
               │ TaskEnvelope
               │
┌──────────────▼──────────────────────────┐
│      Cognify Wrapper Agent              │
│  (agents/cognify_wrapper/app.py)        │
│  - Protocol adapter                     │
│  - Port: 5020                           │
└──────────────┬──────────────────────────┘
               │
               │ AgentInput
               │
┌──────────────▼──────────────────────────┐
│         Cognify Agent                    │
│  (app/agents/cognify_agent.py)          │
│  - LangGraph workflow                   │
│  - Adaptive learning logic              │
└──────────────┬──────────────────────────┘
               │
               │ AgentOutput
               │
┌──────────────▼──────────────────────────┐
│      CompletionReport                   │
│  - next_review_time                     │
│  - difficulty_score                     │
│  - difficulty (enum)                    │
│  - recommendation                       │
└─────────────────────────────────────────┘


### Integration Points

1. *Supervisor Protocol*:
   - Accepts TaskEnvelope from supervisor
   - Returns CompletionReport with results
   - Health check endpoint for agent discovery

2. *Database Integration*:
   - SQLAlchemy ORM for database operations
   - Connection pooling for performance
   - Transaction management

3. *External APIs* (Optional):
   - Google Gemini API (initialized but not actively used)
   - Can be extended for LLM-powered features

---

## Technology Stack

### Backend
- *Framework*: FastAPI 0.104.1
- *Server*: Uvicorn
- *ORM*: SQLAlchemy 2.0.23
- *Database*: SQLite (dev) / PostgreSQL (prod)
- *Authentication*: JWT (python-jose)
- *Password Hashing*: bcrypt (passlib)

### Agent Framework
- *Workflow*: LangGraph 0.0.20
- *LLM Framework*: LangChain 0.1.0
- *LLM Integration*: LangChain Google GenAI 0.0.6
- *LLM Provider*: Google Gemini (gemini-pro)

### Data Processing
- *Numerical*: NumPy 1.24.3
- *Analytics*: Pandas 2.1.4
- *Visualization*: Matplotlib, Seaborn, Plotly

### Frontend
- *Framework*: React with TypeScript
- *UI Library*: Material-UI
- *HTTP Client*: Axios
- *State Management*: React Context API

### Infrastructure
- *Containerization*: Docker
- *Orchestration*: Docker Compose
- *Web Server*: Nginx (production)
- *Cache*: Redis (optional, configured but not used)

---

## Data Flow

### Review Processing Flow


1. User submits review
   POST /flashcards/{id}/review
   {
     "response_accuracy": 0.85,
     "response_time": 12.5
   }
   ↓
2. Router validates request
   - Checks authentication
   - Validates flashcard ownership
   ↓
3. Service loads flashcard
   - Gets current difficulty_score
   - Gets review history
   ↓
4. Service calls Cognify Agent
   AgentInput(
     user_id="123",
     flashcard_id="456",
     response_accuracy=0.85,
     response_time=12.5,
     current_difficulty=0.6
   )
   ↓
5. Agent processes through LangGraph
   analyze_performance → update_schedule → 
   generate_recommendation → share_learning_data
   ↓
6. Agent returns AgentOutput
   {
     "next_review_time": "2024-01-16T10:30:00",
     "difficulty_score": 0.7,
     "difficulty": "medium",
     "recommendation": "Good progress!..."
   }
   ↓
7. Service updates database
   - Updates flashcard.difficulty_score
   - Updates flashcard.difficulty (enum)
   - Updates flashcard.next_review_time
   - Creates ReviewSession record
   ↓
8. Service returns response
   {
     "message": "Review submitted successfully",
     "agent_output": {...},
     "updated_flashcard": {...}
   }
   ↓
9. Frontend updates UI
   - Shows recommendation
   - Updates flashcard display
   - Refreshes analytics


### Flashcard Creation Flow


1. User creates flashcard
   POST /flashcards/
   {
     "front": "What is Python?",
     "back": "A programming language",
     "difficulty": "medium"
   }
   ↓
2. Router validates and authenticates
   ↓
3. Service creates flashcard
   - Sets default difficulty_score = 0.5
   - Sets status = "new"
   - Sets next_review_time = null
   ↓
4. Database saves flashcard
   ↓
5. Response returned to frontend
   ↓
6. Frontend updates flashcard list


### Due Flashcards Retrieval Flow


1. User requests due flashcards
   GET /flashcards/due
   ↓
2. Service queries database
   WHERE next_review_time <= NOW()
      OR next_review_time IS NULL
   ↓
3. Optional filtering by difficulty_score
   - min_difficulty_score
   - max_difficulty_score
   ↓
4. Returns list of due flashcards
   ↓
5. Frontend displays in study interface


---

## Deployment Architecture

### Development Setup


┌─────────────────┐
│   React Dev     │
│   Server        │
│   Port: 3000    │
└────────┬────────┘
         │
         │ API Calls
         │
┌────────▼────────┐
│  FastAPI Dev    │
│  Server         │
│  Port: 3001     │
└────────┬────────┘
         │
┌────────▼────────┐
│   SQLite DB     │
│   cognify.db    │
└─────────────────┘


### Production Setup (Docker Compose)


┌─────────────────────────────────────────┐
│            Nginx (Port 80/443)          │
│         Reverse Proxy / Load Balancer   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      FastAPI App (Port 3001)            │
│  - Main application                      │
│  - API endpoints                         │
└──────┬───────────────────┬───────────────┘
       │                   │
┌──────▼──────┐   ┌───────▼────────┐
│ PostgreSQL  │   │     Redis      │
│ (Port 5432) │   │  (Port 6379)   │
│             │   │  (Optional)    │
└─────────────┘   └────────────────┘


### Docker Services

1. *app*: FastAPI application
   - Builds from Dockerfile
   - Exposes port 3001
   - Connects to PostgreSQL and Redis

2. *db*: PostgreSQL database
   - Persistent volume for data
   - Health checks enabled

3. *redis*: Redis cache (optional)
   - For future caching needs

4. *nginx*: Web server
   - Reverse proxy
   - SSL termination
   - Static file serving

---

## Component Interaction Diagram


┌──────────────┐
│   Frontend   │
│   (React)    │
└──────┬───────┘
       │ HTTP
       │
┌──────▼──────────────────────────────────┐
│         FastAPI Application              │
│  ┌────────────────────────────────────┐  │
│  │  Routers                           │  │
│  │  - auth.router                     │  │
│  │  - flashcards.router               │  │
│  └──────────┬─────────────────────────┘  │
│             │                            │
│  ┌──────────▼─────────────────────────┐  │
│  │  Services                          │  │
│  │  - FlashcardService                │  │
│  │  - AuthService                     │  │
│  │  - AnalyticsService                │  │
│  └──────────┬─────────────────────────┘  │
│             │                            │
│  ┌──────────▼─────────────────────────┐  │
│  │  Cognify Agent                    │  │
│  │  - LangGraph Workflow              │  │
│  │  - Performance Analysis            │  │
│  │  - Spaced Repetition               │  │
│  └────────────────────────────────────┘  │
└──────────────┬───────────────────────────┘
               │
               │ SQLAlchemy ORM
               │
┌──────────────▼──────────────┐
│      Database               │
│  - Users                     │
│  - Flashcards                │
│  - ReviewSessions            │
└─────────────────────────────┘


---

## Security Architecture

### Authentication Flow


1. User Registration
   - Password hashed with bcrypt
   - User stored in database
   
2. User Login
   - Credentials validated
   - JWT token generated
   - Token returned to client
   
3. Authenticated Requests
   - Token in Authorization header
   - Token validated on each request
   - User context extracted
   - Resource access controlled


### Security Measures

- *Password Hashing*: bcrypt with salt
- *JWT Tokens*: Signed with secret key
- *CORS*: Configured for allowed origins
- *SQL Injection*: Prevented by SQLAlchemy ORM
- *Input Validation*: Pydantic models

---

## Performance Considerations

### Optimization Strategies

1. *Database*:
   - Indexed columns (user_id, flashcard_id)
   - Connection pooling
   - Query optimization

2. *Agent Processing*:
   - Async processing with LangGraph
   - Efficient state management
   - Minimal external API calls

3. *Caching* (Future):
   - Redis for frequently accessed data
   - Response caching for analytics

### Scalability

- *Horizontal Scaling*: Stateless API allows multiple instances
- *Database*: PostgreSQL supports concurrent connections
- *Load Balancing*: Nginx can distribute traffic

---

## Error Handling

### Error Flow


Request
  ↓
Validation Error → 400 Bad Request
  ↓
Authentication Error → 401 Unauthorized
  ↓
Authorization Error → 403 Forbidden
  ↓
Not Found Error → 404 Not Found
  ↓
Processing Error → 500 Internal Server Error
  ↓
Response with Error Details


### Error Types

- *Validation Errors*: Pydantic model validation
- *Database Errors*: SQLAlchemy exception handling
- *Agent Errors*: Try-catch with fallback to simulation
- *Authentication Errors*: JWT validation failures

---

## Future Enhancements

### Planned Features

1. *Enhanced Agent*:
   - LLM-powered recommendations
   - Context-aware suggestions
   - Multi-modal learning support

2. *Advanced Analytics*:
   - Predictive learning curves
   - Performance forecasting
   - Comparative analytics

3. *Integration*:
   - Supervisor agent communication
   - Cross-agent learning data sharing
   - Federated learning support

4. *Caching*:
   - Redis integration for hot data
   - Response caching
   - Query result caching

---

## Conclusion

Cognify is built with a modular, scalable architecture that separates concerns across layers. The LangGraph-based agent provides intelligent adaptive learning, while the database layer ensures persistent state management. The system is designed for extensibility and can integrate with larger multi-agent systems.

For more details, refer to:
- [README.md](./README.md) - User guide and setup
- [INTEGRATION.md](../agents/cognify_wrapper/INTEGRATION.md) - Multi-agent integration
- API Documentation: /docs endpoint when running