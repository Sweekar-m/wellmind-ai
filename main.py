"""WellMindAI - Mental Wellness Flask App.

A production-ready mental wellness assistant with:
- User authentication
- Persistent memory (ChromaDB)
- AI-powered conversations
- Mood tracking
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from db import init_db, get_user_by_id
from auth import register_user, authenticate_user, get_user_info
from services.ai_service import get_ai_response
from services.mood_service import detect_mood, get_mood_emoji
from services.session_service import get_or_create_session, get_user_chat_history
from services.memory_service import get_memory_service
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize database
init_db()

# Initialize memory service
memory_service = get_memory_service()


# ==================== AUTHENTICATION ROUTES ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if request.method == "POST":
        try:
            data = request.get_json()
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()
            
            result = register_user(username, email, password)
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 400
            
            session["user_id"] = result["user_id"]
            return jsonify({"success": True, "redirect": "/chat-page"}), 200
        
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({"success": False, "error": "Registration failed"}), 500
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == "POST":
        try:
            data = request.get_json()
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            
            user_id = authenticate_user(username, password)
            
            if not user_id:
                return jsonify({"success": False, "error": "Invalid credentials"}), 401
            
            session["user_id"] = user_id
            return jsonify({"success": True, "redirect": "/chat-page"}), 200
        
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({"success": False, "error": "Login failed"}), 500
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout route."""
    session.clear()
    return redirect(url_for("home"))


# ==================== FRONTEND ROUTES ====================

@app.route("/")
def home():
    """Home page."""
    return render_template("home.html")


@app.route("/chat-page")
def chat_page():
    """Chat page (protected - requires login)."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = get_user_info(session["user_id"])
    return render_template("chat.html", user=user)


# ==================== API ROUTES ====================

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat API endpoint."""
    
    # Check authentication
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    try:
        user_id = session["user_id"]
        data = request.get_json()
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id")
        
        if not user_message:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        if not session_id:
            return jsonify({"success": False, "error": "No session"}), 400
        
        # 1. Detect mood
        mood = detect_mood(user_message)
        
        # 2. Retrieve context from memory (PostgreSQL history)
        context = memory_service.get_context(user_id, user_message, top_k=5)
        
        # 3. Get AI response with context
        result = get_ai_response(user_message, mood, context)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "response": result.get("response", "Error generating response")
            }), 500
        
        ai_response = result["response"]
        
        # 4. Store interaction in memory
        memory_service.store_interaction(user_id, user_message, ai_response, mood)
        
        # 5. Save to database
        from db import save_chat_message
        save_chat_message(user_id, session_id, user_message, ai_response, mood)
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "mood": mood,
            "mood_emoji": get_mood_emoji(mood)
        }), 200
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "response": "An error occurred. Please try again."
        }), 500


@app.route("/api/session/new", methods=["POST"])
def new_session():
    """Create new chat session."""
    
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    try:
        user_id = session["user_id"]
        chat_session = get_or_create_session(user_id)
        
        return jsonify({
            "success": True,
            "session_id": chat_session.session_id
        }), 200
    
    except Exception as e:
        print(f"Session creation error: {e}")
        return jsonify({"success": False, "error": "Failed to create session"}), 500


@app.route("/api/session/history", methods=["GET"])
def get_history():
    """Get chat history for user."""
    
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    try:
        user_id = session["user_id"]
        session_id = request.args.get("session_id")
        
        history = get_user_chat_history(user_id, session_id)
        
        return jsonify({
            "success": True,
            "data": history
        }), 200
    
    except Exception as e:
        print(f"History retrieval error: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve history"}), 500


@app.route("/api/user/info", methods=["GET"])
def get_user():
    """Get current user info."""
    
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    user = get_user_info(session["user_id"])
    
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    return jsonify({
        "success": True,
        "user": user
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


# ==================== STARTUP ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    print(f"Starting WellMindAI on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)
