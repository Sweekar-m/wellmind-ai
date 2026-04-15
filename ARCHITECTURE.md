# WellMindAI - System Architecture 🏗️

## High-Level Overview

WellMindAI is a three-tier mental wellness application:

```
┌────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
│  HTML/CSS/JS • Responsive UI • Real-time Updates           │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  FLASK BACKEND (Python)                    │
│  • Authentication • Chat API • Error Handling              │
└────────────┬──────────────────────────┬───────────────────┘
             │                          │
             ▼                          ▼
    ┌─────────────────────┐  ┌──────────────────────┐
    │   SQLite Database   │  │   ChromaDB Vector    │
    │  • Users            │  │   • Embeddings       │
    │  • Sessions         │  │   • Context Memory   │
    │  • Chat History     │  │   • Similarity Search│
    └─────────────────────┘  └──────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ OpenRouter API / OpenAI    │
        │ • Llama 3.8B Model         │
        │ • LLM Responses            │
        └────────────────────────────┘
```

---

## Component Breakdown

### 1. Frontend Layer (Browser)

#### Files
- `templates/home.html` — Landing page
- `templates/login.html` — Auth form
- `templates/register.html` — Auth form
- `templates/chat.html` — Chat UI
- `static/style.css` — Styling (1000+ lines)
- `static/script.js` — Logic & API calls

#### Responsibilities
- Render UI components
- Handle user input
- Make API calls
- Update DOM dynamically
- Display typing indicators
- Show mood indicators
- Track session statistics

#### Technologies
- HTML5 semantic markup
- CSS3 animations & transitions
- Vanilla JavaScript (no frameworks)
- Fetch API for HTTP requests
- LocalStorage for temporary data

---

### 2. Flask Backend Layer

#### Main Application (`main.py`)

```
Flask App
├── Authentication Routes
│   ├── POST /register
│   ├── POST /login
│   └── GET /logout
│
├── Frontend Routes (return HTML)
│   ├── GET / → home.html
│   ├── GET /chat-page → chat.html
│   ├── GET /login → login.html
│   └── GET /register → register.html
│
└── API Routes (return JSON)
    ├── POST /api/chat → Send message
    ├── POST /api/session/new → Create session
    ├── GET /api/session/history → Get history
    └── GET /api/user/info → Get user info
```

#### Request Flow

```
User sends message
    ↓
Frontend: /api/chat (POST)
    ↓
Backend: main.py receives request
    ↓
1. Check authentication (session validation)
    ↓
2. Extract message & session_id
    ↓
3. Call mood_service.detect_mood() → "Stress"/"Sadness"/"Neutral"
    ↓
4. Call memory_service.get_context() → Retrieve past interactions
    ↓
5. Call ai_service.get_ai_response(context) → OpenRouter API
    ↓
6. Call memory_service.store_interaction() → Save to ChromaDB
    ↓
7. Call db.save_chat_message() → Save to SQLite
    ↓
8. Return JSON response with:
    - AI response text
    - Detected mood
    - Mood emoji
    ↓
Frontend displays response
```

---

### 3. Database Layer

#### SQLite (Relational Data)

**Schema:**

```sql
-- User Accounts
users
├── id INT PRIMARY KEY
├── username TEXT UNIQUE
├── email TEXT UNIQUE
├── password_hash TEXT
└── created_at TIMESTAMP

-- Chat Sessions
sessions
├── id INT PRIMARY KEY
├── user_id INT (FK → users)
├── created_at TIMESTAMP
├── updated_at TIMESTAMP
└── mood TEXT

-- Message History
chat_history
├── id INT PRIMARY KEY
├── user_id INT (FK → users)
├── session_id INT (FK → sessions)
├── user_message TEXT
├── ai_response TEXT
├── mood TEXT
└── created_at TIMESTAMP
```

**Functions** (`db.py`):
- `init_db()` — Initialize tables
- `get_user_by_username()` — Auth check
- `create_user()` — User registration
- `create_session()` — New chat session
- `save_chat_message()` — Store interaction

---

#### ChromaDB (Vector Memory)

**Purpose:**
Store message embeddings for semantic search

**Collections:**
```
Collection per user: user_1, user_2, etc.
│
├── Document (message pair)
│   ├── ID: msg_1234567890
│   ├── Text: "User: I feel sad\nAssistant: I hear you..."
│   └── Metadata:
│       ├── user_message: "I feel sad"
│       ├── ai_response: "I hear you..."
│       ├── mood: "Sadness"
│       └── timestamp: "2026-04-15T10:30:00"
│
└── Embeddings (vector representation)
    ├── Computed by: sentence-transformers
    ├── Vector size: 384 dimensions
    └── Used for: similarity search
```

**Operations:**
- `store_interaction()` — Add new message + embedding
- `get_context()` — Retrieve top-3 similar messages
- `get_collection()` — Get/create user collection

---

### 4. Service Layer

#### Mood Service (`services/mood_service.py`)

```
detect_mood(text) → "Stress" / "Sadness" / "Neutral"

Stress Keywords:
├── "stress", "anxious", "overwhelmed"
├── "pressure", "frustrated", "rush"
└── "burned out", "panic", "nervous"

Sadness Keywords:
├── "sad", "lonely", "hurt", "depressed"
├── "miserable", "unhappy", "down", "blue"
└── "hopeless", "empty", "devastated"

Default: "Neutral" (if no keywords match)

get_mood_emoji(mood) → "😰" / "😔" / "😊"
```

#### AI Service (`services/ai_service.py`)

```
get_ai_response(message, mood, context) → {
    "success": bool,
    "response": "AI response text",
    "error": "error_code" (if failed)
}

Process:
├── Validate API key
├── Build prompt with:
│   ├── System prompt (empathetic AI)
│   ├── Past context (top-3 memories)
│   ├── Current mood
│   └── User message
├── Call OpenRouter API:
│   ├── Model: meta-llama/llama-3-8b-instruct
│   ├── Temperature: 0.7
│   ├── Max tokens: 150
│   └── Timeout: 30s
├── Handle HTTP errors:
│   ├── 429 → Rate limited
│   ├── 401/403 → Auth failed
│   ├── 500+ → Server error
│   └── Timeout → Network issue
└── Return response or error
```

#### Memory Service (`services/memory_service.py`)

```
MemoryService

├── get_collection(user_id)
│   └── Returns ChromaDB collection for user
│
├── store_interaction(user_id, user_msg, ai_msg, mood)
│   └── Embeds and stores new message pair
│
├── get_context(user_id, message, top_k=3)
│   ├── Embeds current message
│   ├── Searches for similar past messages
│   ├── Returns top-3 results as context
│   └── Formatted for LLM prompt injection
│
├── delete_user_memory(user_id)
│   └── For privacy: delete all user embeddings
│
└── get_user_memory_stats(user_id)
    └── Returns interaction count

Embeddings:
├── Model: sentence-transformers (all-MiniLM-L6-v2)
├── Dimensions: 384
├── Processing: Automatic via ChromaDB
└── Similarity: Cosine distance
```

#### Session Service (`services/session_service.py`)

```
ChatSession

├── __init__(session_id)
│   └── Track start time
│
├── add_message(mood)
│   ├── Increment message count
│   └── Record mood for this message
│
├── get_stats()
│   ├── message_count
│   ├── duration_sec
│   ├── dominant_mood
│   └── mood_breakdown {}
│
└── get_duration_minutes()
    └── Calculate session length
```

---

### 5. Authentication Layer (`auth.py`)

```
register_user(username, email, password)
├── Validate inputs:
│   ├── Username: 3-20 chars, alphanumeric + underscore
│   ├── Email: Valid email format
│   └── Password: Min 6 characters
├── Check for duplicates in database
├── Hash password with PBKDF2
├── Insert into users table
└── Return user_id or error

authenticate_user(username, password)
├── Get user from database
├── Compare provided password with stored hash
└── Return user_id if match, None otherwise

get_user_info(user_id)
├── Fetch user from database
└── Return {id, username, email}
```

---

## Data Flow Example

### Scenario: User sends "I feel really stressed"

```
1. Browser: User types message, clicks send
   └─→ JavaScript captures input

2. Frontend: JavaScript sends POST request
   ```json
   POST /api/chat
   {
     "message": "I feel really stressed",
     "session_id": 1
   }
   ```

3. Backend: Flask receives request
   └─→ Extracts: message, session_id, user_id from session

4. Mood Detection: services/mood_service.py
   ```
   Input: "I feel really stressed"
   Keywords found: "stressed" (stress keyword)
   Output: "Stress"
   ```

5. Memory Retrieval: services/memory_service.py
   ```
   Query: "I feel really stressed" → embedding vector
   ChromaDB search: Find 3 most similar past messages
   Result: 
   - "Work is overwhelming" (similar)
   - "Feeling anxious today" (similar)
   - "Lot of pressure" (similar)
   ```

6. Prompt Building:
   ```
   System: "You are WellMindAI, calm and supportive..."
   
   Context:
   [Past - Mood: Stress]
   User: Work is overwhelming
   Assistant: That sounds intense...
   
   [Past - Mood: Stress]
   User: Feeling anxious today
   Assistant: Anxiety can feel heavy...
   
   [Current mood: Stress]
   User: I feel really stressed
   ```

7. AI Generation: services/ai_service.py
   ```
   → OpenRouter API (Llama 3.8B)
   → Generate response (1-2 seconds)
   ← "That sounds challenging. Sometimes taking small breaks..."
   ```

8. Storage: Both databases
   ```
   SQLite: INSERT INTO chat_history
   - user_message: "I feel really stressed"
   - ai_response: "That sounds challenging..."
   - mood: "Stress"
   
   ChromaDB: Add embeddings
   - Store new interaction
   - Make available for future context
   ```

9. Response to Frontend:
   ```json
   {
     "success": true,
     "response": "That sounds challenging...",
     "mood": "Stress",
     "mood_emoji": "😰"
   }
   ```

10. Frontend Update:
    - Add user message bubble (green, right-aligned)
    - Add AI message bubble (white, left-aligned)
    - Update mood indicator: "😰 Stress"
    - Increment message count: "Messages: 2"
    - Update duration: "Duration: 1m 23s"
    - Scroll to bottom
    - Enable input field

```

---

## Security Architecture

```
┌──────────────────────────────────────────┐
│         Client-Side Protection           │
├──────────────────────────────────────────┤
│ • HTML escaping for XSS prevention       │
│ • HTTPS only (enforced by Render)        │
└────────────────┬─────────────────────────┘
                 │
┌────────────────▼─────────────────────────┐
│    Transport Layer (HTTPS/TLS)           │
│ • Encrypted communication                │
│ • Certificate validation                 │
└────────────────┬─────────────────────────┘
                 │
┌────────────────▼─────────────────────────┐
│       Flask Application Layer            │
├──────────────────────────────────────────┤
│ • Session validation on protected routes │
│ • CSRF token support                     │
│ • Error logging without info leakage     │
└────────────────┬─────────────────────────┘
                 │
┌────────────────▼─────────────────────────┐
│       Backend Services Layer             │
├──────────────────────────────────────────┤
│ • Password hashing (PBKDF2 + salt)       │
│ • Per-user memory isolation              │
│ • API key in environment (not hardcoded) │
│ • Input validation on all endpoints      │
└────────────────┬─────────────────────────┘
                 │
┌────────────────▼─────────────────────────┐
│     Database & External Services         │
├──────────────────────────────────────────┤
│ • SQLite on local/sandboxed filesystem   │
│ • ChromaDB vector DB (local)             │
│ • OpenRouter API (rate limiting)         │
└──────────────────────────────────────────┘
```

---

## Performance Optimization

### Caching Strategy

```
User Session
├── Message Cache (in memory)
│   └── Recent 10-20 messages
│
├── User Info Cache (30 min TTL)
│   └── User profile data
│
└── Vector Cache
    └── ChromaDB handles internally
```

### Query Optimization

```
Database:
├── User lookup: Indexed by username/id
├── Session queries: Indexed by user_id
└── Chat history: Indexed by session_id + created_at

ChromaDB:
├── Vector search: Efficient approximate nearest neighbors
├── Top-K retrieval: Returns only top 3 results
└── Lazy loading: Load embeddings on-demand
```

### Frontend Optimization

```
├── Lazy loading of CSS/JS
├── Hardware-accelerated animations
├── Debounced API calls (no spam)
├── Image optimization (emoji only, no PNG)
└── Minimal DOM manipulation
```

---

## Deployment Architecture

```
GitHub Repository
    ↓
    ├─→ Render.com (Web Service)
    │   ├── Run: Gunicorn
    │   ├── Environment: Python 3.11
    │   └── Storage: Ephemeral filesystem
    │
    ├─→ PostgreSQL (Optional)
    │   └── Persistent database
    │
    └─→ External APIs
        └── OpenRouter API
            └── LLM inference
```

---

## Error Handling Flow

```
Request comes in
    ↓
try:
    ├── Authenticate user
    ├── Validate input
    ├── Call external services
    └── Process and respond
except AuthenticationError:
    → Return 401 with message
except ValidationError:
    → Return 400 with message
except RateLimitError:
    → Return 429 with friendly message
except TimeoutError:
    → Return 504 with friendly message
except Exception:
    → Return 500 with generic message
    → Log full error to server logs
```

---

## Monitoring & Observability

```
Application Monitoring

├── Logs
│   ├── Error logs → Find crashes
│   ├── Access logs → Track usage
│   └── Debug logs (dev mode) → Development
│
├── Metrics
│   ├── Response time
│   ├── API calls per minute
│   ├── Error rate
│   ├── Memory usage
│   └── Database connections
│
└── Alerts
    ├── High error rate
    ├── Response time > 5s
    ├── Memory > 500MB
    └── Failed health check
```

---

## Conclusion

WellMindAI is built with:
- ✅ Clean separation of concerns
- ✅ Scalable architecture
- ✅ Production-ready security
- ✅ Modern tech stack
- ✅ Comprehensive error handling
- ✅ Performance optimization

Perfect for deployment and future growth!

---

**Last Updated:** April 2026
