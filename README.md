# WellMindAI 🌿

A production-ready mental wellness web application powered by AI. Chat with an empathetic AI assistant that understands your emotions, tracks your mood, and provides personalized support.

**Live Demo:** Deployed on https://wellmind-ai-odam.onrender.com

---

## Features ✨

- **🔐 Secure Authentication**
  - User registration and login with password hashing
  - Flask sessions for secure access
  - Protected chat endpoints

- **🧠 Intelligent Mood Detection**
  - Real-time mood analysis (Stress, Sadness, Neutral)
  - Keyword-based emotion recognition
  - Visual mood indicators

- **💬 AI-Powered Conversations**
  - OpenRouter API integration (Llama 3.8B model)
  - Empathetic, concise responses
  - Context-aware conversations

- **📚 Persistent Memory (ChromaDB)**
  - Vector embeddings of conversations
  - User-specific memory isolation
  - Context injection from past interactions
  - Semantic similarity search

- **📊 Session Tracking**
  - Message count tracking
  - Duration monitoring
  - Dominant mood analysis
  - Mood breakdown visualization

- **🎨 Modern, Responsive UI**
  - Mobile-first design
  - Smooth animations
  - Glassmorphism effects
  - Accessibility-focused

---

## Tech Stack 🛠️

**Backend:**
- Python 3.11
- Flask — Web framework
- SQLite — User database
- ChromaDB — Vector database for memories
- sentence-transformers — Embeddings
- OpenRouter API — AI model access

**Frontend:**
- HTML5
- CSS3 (modern features)
- Vanilla JavaScript (no frameworks)

**Deployment:**
- Gunicorn — WSGI server
- Render.com — Cloud hosting
- Environment variables — Configuration

---

## Installation & Setup 🚀

### Prerequisites
- Python 3.11+
- pip
- OpenRouter API key (free at https://openrouter.ai/keys)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd wellmind
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # - OPENROUTER_API_KEY=your_key_here
   # - SECRET_KEY=your_secret_key
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Visit: http://localhost:5000

---

## Deployment on Render.com 🌐

### Step 1: Prepare Repository

Ensure your repo has:
- ✅ `requirements.txt` with all dependencies
- ✅ `Procfile` with gunicorn command
- ✅ `runtime.txt` with Python version
- ✅ `.env.example` as template

### Step 2: Create Render Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** wellmind-ai
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment**:
```
OPENROUTER_API_KEY=sk_....
SECRET_KEY=generate-a-strong-random-key-here
FLASK_ENV=production
DATABASE_PATH=wellmind.db
CHROMA_DB_PATH=./chroma_data
```

### Step 4: Deploy

- Click "Deploy" and wait for build completion
- Your app will be available at: `https://wellmind-ai.onrender.com`

---

## Project Structure 📁

```
wellmind/
├── main.py                 # Flask app & routes
├── db.py                   # Database management
├── auth.py                 # Authentication helpers
│
├── services/
│   ├── ai_service.py       # OpenRouter API integration
│   ├── mood_service.py     # Mood detection
│   ├── memory_service.py   # ChromaDB management
│   └── session_service.py  # Chat session management
│
├── templates/
│   ├── home.html           # Landing page
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   └── chat.html           # Chat interface
│
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
│
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn configuration
├── runtime.txt             # Python version
├── .env.example            # Environment template
└── README.md               # This file
```

---

## API Endpoints 🔌

### Authentication
- `POST /register` — Register new user
- `POST /login` — Login user
- `GET /logout` — Logout user

### Chat
- `POST /api/chat` — Send message to AI
- `POST /api/session/new` — Create new chat session
- `GET /api/session/history` — Get chat history
- `GET /api/user/info` — Get user information

---

## Environment Variables 🔑

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | `sk_...` |
| `SECRET_KEY` | Flask session secret | `your-random-key` |
| `FLASK_ENV` | Environment mode | `production` |
| `DATABASE_PATH` | SQLite database location | `wellmind.db` |
| `CHROMA_DB_PATH` | Vector database location | `./chroma_data` |
| `PORT` | Server port | `5000` |

---

## User Flow 👤

1. **Registration/Login**
   - New users register with username, email, password
   - Passwords are hashed with werkzeug.security
   - Existing users login with credentials

2. **Chat Session**
   - User starts new session
   - Inputs message
   - System detects mood from keywords
   - AI retrieves similar past messages for context
   - OpenRouter API generates response
   - Interaction stored in ChromaDB
   - Response shown with mood emoji

3. **Session Tracking**
   - Real-time message count
   - Duration timer
   - Dominant mood indicator

---

## Mood Detection 🧠

The system recognizes three mood categories:

| Mood | Keywords | Emoji |
|------|----------|-------|
| **Stress** | pressure, anxious, overwhelmed, busy, rush | 😰 |
| **Sadness** | sad, lonely, hurt, depressed, miserable | 😔 |
| **Neutral** | everything else | 😊 |

---

## AI System Prompt 🤖

```
You are WellMindAI, a calm and supportive mental wellness assistant.

Guidelines:
- Be empathetic, kind, and human-like
- Keep responses concise (2-3 sentences max)
- Focus exclusively on emotions and feelings
- Avoid unrelated topics
- Acknowledge feelings first, then offer support
- Use warm, conversational language
```

---

## Database Schema 📊

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  email TEXT UNIQUE,
  password_hash TEXT,
  created_at TIMESTAMP
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  mood TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Chat History Table
```sql
CREATE TABLE chat_history (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  session_id INTEGER,
  user_message TEXT,
  ai_response TEXT,
  mood TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

## Error Handling ⚠️

The application gracefully handles:

- ✅ API rate limiting (429)
- ✅ Authentication errors (401, 403)
- ✅ Server errors (500+)
- ✅ Network timeouts
- ✅ Missing API key
- ✅ Empty messages
- ✅ Invalid credentials

---

## Performance Optimization ⚡

- **ChromaDB Caching**: Vector embeddings cached locally
- **Message Pagination**: Only loads relevant context
- **Lazy Loading**: Assets loaded on demand
- **CSS Animation**: Hardware-accelerated transforms
- **Frontend Debouncing**: Rate-limited API calls

---

## Security Features 🔒

- ✅ Password hashing with Werkzeug
- ✅ CSRF protection via Flask sessions
- ✅ XSS prevention (HTML escaping)
- ✅ Per-user memory isolation
- ✅ Secure API endpoints (session validation)
- ✅ HTTPS enforced in production

---

## Troubleshooting 🔧

### "API key not configured"
- Add `OPENROUTER_API_KEY` to `.env`
- Restart the application

### "Chrome Database not found"
- Ensure `CHROMA_DB_PATH` is writable
- Check directory permissions

### "Session not created"
- Verify database is initialized
- Check SQLite permissions

### "Slow responses"
- Check OpenRouter API status
- Reduce `top_k` in `memory_service.py`
- Look for network latency

---

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License 📄

This project is open source. Feel free to use and modify for personal or commercial use.

---

## Support 💬

For issues or questions:
- Check the troubleshooting section
- Review server logs in Render dashboard
- Test locally before deploying

---

## Roadmap 🗺️

- [ ] Voice input/output
- [ ] Conversation analytics dashboard
- [ ] Mood insights & trends
- [ ] Export conversation history
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Therapist integration

---

**Built with ❤️ for mental wellness.**
# wellmind-ai
