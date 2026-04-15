# Local Testing Guide 🧪

## Prerequisites

- Python 3.11+
- pip package manager
- OpenRouter API key (free from https://openrouter.ai/keys)
- Text editor or IDE

---

## Setup for Local Testing

### 1. Clone/Navigate to Project

```bash
cd d:\wellmind
```

### 2. Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected packages:
- Flask 3.0.0
- requests 2.31.0
- chromadb 0.4.24
- sentence-transformers 2.2.2
- python-dotenv 1.0.0
- werkzeug 3.0.1
- gunicorn 21.2.0

### 4. Configure Environment

Create `.env` in the project root:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENROUTER_API_KEY=sk_or_YOUR_ACTUAL_API_KEY_HERE
SECRET_KEY=your-random-secret-key-here
FLASK_DEBUG=True
FLASK_ENV=development
```

Get OpenRouter API key:
1. Go to https://openrouter.ai/keys
2. Create account or login
3. Copy your API key

### 5. Initialize Database

```bash
python -c "from db import init_db; init_db(); print('✅ Database initialized')"
```

You should see: `✅ Database initialized`

---

## Running the App

### Start Flask Server

```bash
python main.py
```

Expected output:
```
Starting WellMindAI on port 5000...
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Access in Browser

Open: http://localhost:5000

---

## Testing Workflow

### 1. Test Home Page
- [ ] Visit http://localhost:5000
- [ ] See hero section, features, trust indicators
- [ ] Click "Start Chat" → redirects to login
- [ ] Click "Learn More" → page scrolls

### 2. Test Registration
- [ ] Click "Register" in header
- [ ] Fill form with:
  - Username: `testuser123`
  - Email: `test@example.com`
  - Password: `testpass123`
- [ ] Submit
- [ ] Should redirect to /chat-page

### 3. Test Login
- [ ] Go to /logout
- [ ] Go to /login
- [ ] Enter credentials from above
- [ ] Submit
- [ ] Should see chat interface

### 4. Test Chat Functionality
- [ ] Type: "I'm feeling really stressed about work"
- [ ] Click send or press Enter
- [ ] See typing indicator
- [ ] AI responds (should mention stress/pressure)
- [ ] Mood shows 😰 (Stress)
- [ ] Message count: 2

### 5. Test Mood Detection
Send different messages and verify mood:

**Stress messages:**
```
"I feel so overwhelmed with everything"
"So much pressure and anxiety"
"I'm burned out and exhausted"
```
Expected: 😰 Stress

**Sadness messages:**
```
"I feel really lonely right now"
"I'm so depressed and hopeless"
"Everything makes me sad"
```
Expected: 😔 Sadness

**Neutral messages:**
```
"Tell me about meditation"
"How do I stay positive?"
"What's a good hobby?"
```
Expected: 😊 Neutral

### 6. Test Persistent Memory
- [ ] Have 3-4 conversations
- [ ] Later mention a previous topic
- [ ] AI should reference previous context
- [ ] Example:
  - First: "I'm stressed about my job"
  - Later: "You remembered I mentioned work issues!"

### 7. Test Session Features
- [ ] Check stats update in real-time:
  - Message count increases
  - Duration timer counts up
  - Mood updates with each message

### 8. Test Error Handling
Try these to trigger errors:

**Empty message:**
- Click send without typing
- Should show error or prevent submission

**Missing API key:**
- Remove OPENROUTER_API_KEY from .env
- Try to chat
- Should show friendly error message

**Invalid credentials:**
- Try login with wrong password
- Should show "Invalid credentials"

**Duplicate username:**
- Register with same username twice
- Should show "Username already exists"

---

## Browser DevTools Testing

### 1. Check Network Requests
- Open DevTools (F12)
- Go to Network tab
- Send a message
- You should see:
  - `POST /api/chat` → 200 response
  - `POST /api/session/new` → 200 response
  - `GET /api/user/info` → 200 response

### 2. Check Console for Errors
- DevTools Console tab
- Should show no JavaScript errors
- Look for any warnings

### 3. Check Application Storage
- Application tab
- Cookies: Should see Flask `session` cookie
- Local Storage: Empty (OK)

---

## Database Inspection

### View SQLite Database

```bash
# Install sqlite3 CLI if needed
# Windows: comes with Python

# Open the database
sqlite3 wellmind.db

# Commands:
.tables                           # List all tables
SELECT * FROM users;              # View users
SELECT * FROM sessions;           # View sessions
SELECT * FROM chat_history;       # View conversations
.exit                             # Exit
```

### Verify Data

After testing, check:
```sql
-- Count users
SELECT COUNT(*) FROM users;

-- Get conversation history
SELECT user_message, ai_response, mood, created_at 
FROM chat_history 
ORDER BY created_at DESC 
LIMIT 5;

-- Check mood distribution
SELECT mood, COUNT(*) 
FROM chat_history 
GROUP BY mood;
```

---

## Memory System Testing

### Check ChromaDB

```python
from services.memory_service import get_memory_service

memory = get_memory_service()

# Get user's memory stats
stats = memory.get_user_memory_stats(user_id=1)
print(f"Total interactions stored: {stats['total_interactions']}")

# Retrieve context for a message
context = memory.get_context(user_id=1, current_message="I feel sad", top_k=3)
print(f"Retrieved context:\n{context}")
```

---

## Performance Testing

### Measure Response Time

```bash
# Time a curl request
time curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":1}'
```

Expected:
- Cold response: 2-5 seconds
- Warm response: 1-2 seconds
- Database query: <10ms
- Memory search: <50ms

---

## Mobile Testing

### Test Responsive Design

1. **Chrome DevTools:**
   - F12 → Toggle Device Toolbar (Ctrl+Shift+M)
   - Test: iPhone 12, iPad, Galaxy S21

2. **Verify:**
   - Text is readable at all sizes
   - Buttons are clickable (48px minimum)
   - Chat bubbles fit on screen
   - Input area visible without scrolling

---

## Security Testing

### Test Authentication

```bash
# Try accessing chat without login
curl http://localhost:5000/chat-page
# Should redirect to login

# Try logout
curl http://localhost:5000/logout
# Should redirect to home
```

### Test XSS Protection

Send message:
```
<script>alert('XSS')</script>
```

Should display as text, not execute.

### Test SQL Injection

Try registration with:
```
Username: admin'; DROP TABLE users; --
```

Should fail gracefully (username validation).

---

## Cleanup

### Stop Server
- Press `Ctrl+C` in terminal

### Deactivate Virtual Environment
```bash
deactivate
```

### Remove Test Data
```bash
# Delete database
rm wellmind.db

# Delete vector embeddings
rm -rf chroma_data

# Restart to recreate empty database
python main.py
```

---

## Common Issues & Solutions

### Issue: "No module named 'chromadb'"
**Solution:**
```bash
pip install chromadb sentence-transformers
```

### Issue: "OPENROUTER_API_KEY not found"
**Solution:**
```bash
# Create .env file
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

### Issue: Port 5000 already in use
**Solution:**
```bash
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000

# Then kill the process or use different port:
PORT=5001 python main.py
```

### Issue: Database locked
**Solution:**
```bash
# Remove lock files
rm wellmind.db-journal
# Delete and recreate
rm wellmind.db
```

---

## Automated Testing (Optional)

Create `test_app.py`:

```python
import unittest
from main import app

class TestWellMindAI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_get(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_get(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

Run:
```bash
python -m unittest test_app.py
```

---

## Success Checklist ✅

- [ ] App starts without errors
- [ ] Home page loads
- [ ] Registration works
- [ ] Login works
- [ ] Chat interface appears
- [ ] Messages send successfully
- [ ] AI responds appropriately
- [ ] Mood detection works
- [ ] Stats update in real-time
- [ ] No console errors
- [ ] Database contains data
- [ ] Logout works
- [ ] Mobile view responsive

---

## Next Step: Deployment

Once all tests pass locally:

1. Push to GitHub
2. Create Render service
3. Add environment variables
4. Deploy

See `DEPLOYMENT.md` for details.

---

Happy testing! 🚀
