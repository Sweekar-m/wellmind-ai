"""Authentication utilities."""

from werkzeug.security import generate_password_hash, check_password_hash
from db import get_user_by_username, create_user, get_user_by_id
import re


def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_username(username):
    """Validate username (3-20 chars, alphanumeric + underscore)."""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None


def is_valid_password(password):
    """Validate password (min 6 chars)."""
    return password and len(password) >= 6


def register_user(username, email, password):
    """Register a new user. Returns user_id or error message."""
    
    # Validate inputs
    if not is_valid_username(username):
        return {"error": "Username must be 3-20 characters, alphanumeric + underscore"}
    
    if not is_valid_email(email):
        return {"error": "Invalid email format"}
    
    if not is_valid_password(password):
        return {"error": "Password must be at least 6 characters"}
    
    # Check if user exists
    if get_user_by_username(username):
        return {"error": "Username already exists"}
    
    # Create user
    password_hash = generate_password_hash(password)
    user_id = create_user(username, email, password_hash)
    
    if user_id:
        return {"success": True, "user_id": user_id}
    else:
        return {"error": "Username or email already exists"}


def authenticate_user(username, password):
    """Authenticate user. Returns user_id or None."""
    user = get_user_by_username(username)
    
    if user and check_password_hash(user["password_hash"], password):
        return user["id"]
    
    return None


def get_user_info(user_id):
    """Get user information."""
    user = get_user_by_id(user_id)
    
    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    
    return None
