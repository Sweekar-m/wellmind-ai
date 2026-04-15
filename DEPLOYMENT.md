# Render.com Deployment Guide 🚀

## Prerequisites
- GitHub account with the repository pushed
- Render.com account (free tier available)
- OpenRouter API key

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure these files are in your repository root:
```
✅ requirements.txt     (all dependencies)
✅ Procfile             (web: gunicorn main:app)
✅ runtime.txt          (python-3.11.9)
✅ main.py              (Flask app)
✅ .env.example         (template for env vars)
✅ .gitignore           (excludes .env, __pycache__, etc.)
```

### 2. Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 3. Create Render Web Service

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

2. **Connect Repository:**
   - Select "GitHub"
   - Authorize Render to access your GitHub
   - Search and select your repository
   - Click "Connect"

3. **Configure Service:**

   | Setting | Value | Notes |
   |---------|-------|-------|
   | **Name** | `wellmind-ai` | Becomes part of your URL |
   | **Environment** | Python 3 | Default OK |
   | **Region** | Frankfurt (closest to you) | For lower latency |
   | **Branch** | main | Or your default branch |
   | **Build Command** | `pip install -r requirements.txt` | Installs dependencies |
   | **Start Command** | `gunicorn main:app` | Runs the app |

4. **Choose Plan:**
   - **Free** ($0/month) — Good for testing
   - **Paid** ($7+/month) — Recommended for production

5. **Click "Create Web Service"**

### 4. Add Environment Variables

After service is created, go to **Settings → Environment**:

```
OPENROUTER_API_KEY
sk_or_YOUR_API_KEY_HERE
```

Get from: https://openrouter.ai/keys

```
SECRET_KEY
generate-a-random-string-min-32-chars
```

Example:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```
FLASK_ENV
production
```

```
DATABASE_PATH
wellmind.db
```

```
CHROMA_DB_PATH
./chroma_data
```

Click **"Save"** after adding each variable.

### 5. Deploy

- Render automatically deploys when you push to GitHub
- Or click **"Deploy latest commit"** button
- Check **"Logs"** tab for build progress
- Wait for **"Your service is live"** message

### 6. Access Your App

Your app will be available at:
```
https://wellmind-ai.onrender.com
```

Or whatever name you chose.

---

## Important Notes ⚠️

### Cold Starts
- Free tier sleeps after 15 minutes of inactivity
- First request takes 10-30 seconds to wake up
- Paid plan runs continuously

### Data Persistence
- SQLite database is **ephemeral** on Render
- Data lost when service restarts
- For persistent data, upgrade to PostgreSQL

### Monitoring
- Check **"Logs"** tab for errors
- Use **"Metrics"** to monitor performance
- Set up email alerts in Settings

### SSL/TLS
- Render provides free SSL certificates
- All connections automatically HTTPS

---

## Database Migration to PostgreSQL (Optional)

For production with persistent data:

1. Go to Render Dashboard → Databases
2. Create new PostgreSQL database
3. Update Render service with connection string
4. Modify `db.py` to use PostgreSQL (psycopg2)
5. Redeploy

---

## Troubleshooting 🔧

### Build Fails
- Check **"Logs"** for error messages
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` and `runtime.txt` are properly formatted

### App Crashes
- Check environment variables are set
- Look for missing imports or syntax errors
- Verify OpenRouter API key is valid

### Memory Issues
- Reduce ChromaDB vector search results
- Upgrade to paid plan for more memory

### Slow Response
- Check OpenRouter API response time
- Try different AI model with faster inference
- Upgrade Render plan for more CPU

---

## Cost Estimation 💰

| Component | Free | Pro |
|-----------|------|-----|
| Render Web Service | $0 | $7-25/month |
| Database (if added) | — | $15/month |
| OpenRouter API | Free tier OK | Pay-per-token |
| **Total** | ~$0* | $20-50/month |

*+ OpenRouter usage costs

---

## GitHub Actions for Auto-Deploy

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }}
```

Add secrets in GitHub:
- `RENDER_SERVICE_ID` — from Render URL
- `RENDER_API_KEY` — from Render Account Settings

---

## Monitoring in Production

### Set Up Alerts
- Go to Settings → Notifications
- Enable email alerts for service issues

### Check Status
```bash
curl https://wellmind-ai.onrender.com/
```

Should return HTML of home page.

### View Logs
```bash
# Tail logs in real-time
curl https://api.render.com/logs/srv-[SERVICE_ID]?key=[API_KEY]
```

---

## Next Steps ✅

1. ✅ Deploy to Render
2. ✅ Test all features
3. ✅ Set up custom domain (optional)
4. ✅ Configure monitoring
5. ✅ Add more AI models/features
6. ✅ Scale to production

---

Happy deploying! 🚀
