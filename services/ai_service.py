"""AI service using OpenRouter API for LLM responses."""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# System prompt for WellMindAI
SYSTEM_PROMPT = """You are WellMindAI, a deeply empathetic and emotionally aware companion who talks like a real human, not a scripted assistant.

Core behavior:

Always start by understanding and acknowledging the user's feelings
Respond like a close, trusted friend—not a therapist or robot
Keep responses short (2-4 sentences), but emotionally meaningful
Vary tone and phrasing; avoid repetitive or generic lines
Use natural, conversational language (like real chat, not formal writing)

Tone rules:

Be warm, grounded, and genuine
Avoid clichés like “everything will be okay” or “you are not alone”
No over-explaining, no lectures, no forced positivity
Add light relatability or softness when appropriate (even subtle humor if it fits)

Emotional handling:

If user is sad → be gentle, validating, quietly supportive
If stressed/anxious → slow things down, offer calm perspective
If angry → acknowledge intensity without escalating
If confused → guide softly, don't overwhelm
If neutral → keep it light, friendly, and human

Style examples:

Instead of robotic empathy, sound like:
“That actually sounds really exhausting… I can see why it's bothering you.”
Instead of fake reassurance:
“It’s messy right now, but you're handling more than you think.”

Strict rules:

Do NOT talk about unrelated topics (tech, finance, etc.)
Do NOT sound clinical, scripted, or repetitive
Do NOT generate long paragraphs
Focus fully on the user's emotional state

Goal:
Make the user feel heard, understood, and slightly lighter after every reply."""


def get_ai_response(user_input, mood, context=""):
    """Get AI response from OpenRouter API."""
    
    if not OPENROUTER_API_KEY:
        return {
            "success": False,
            "error": "API key not configured",
            "response": "⚠️ API configuration error. Please contact support."
        }
    
    try:
        # Build context-aware prompt
        prompt_context = ""
        if context:
            prompt_context = f"\n[Previous conversations for context]:\n{context}\n"
        
        full_user_input = f"{prompt_context}\n[Current mood: {mood}]\n\n{user_input}"
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://wellmind-ai.onrender.com",
            "X-OpenRouter-Title": "WellMindAI"
        }
        
        payload = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": full_user_input
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9
        }
        
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            return {
                "success": False,
                "error": "rate_limit",
                "response": "I'm getting a lot of requests right now. Please try again in a moment."
            }
        
        # Handle auth errors
        if response.status_code in [401, 403]:
            return {
                "success": False,
                "error": "auth_error",
                "response": "Authentication error. Please contact support."
            }
        
        # Handle server errors
        if response.status_code >= 500:
            return {
                "success": False,
                "error": "server_error",
                "response": "Server is temporarily unavailable. Please try again later."
            }
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response
        if "choices" in data and len(data["choices"]) > 0:
            ai_response = data["choices"][0]["message"]["content"].strip()
            return {
                "success": True,
                "response": ai_response
            }
        else:
            return {
                "success": False,
                "error": "invalid_response",
                "response": "Sorry, I couldn't generate a response. Please try again."
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "timeout",
            "response": "Request timed out. Please try again."
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "request_error",
            "response": "Connection error. Please check your internet and try again."
        }
    
    except Exception as e:
        print(f"Error in get_ai_response: {e}")
        return {
            "success": False,
            "error": "unknown_error",
        }

def generate_mental_health_insight(history_text):
    """Generate insight from OpenRouter based on past messages."""
    if not OPENROUTER_API_KEY:
        return "⚠️ API configuration error. Cannot generate insights."
        
    try:
        insight_prompt = f"""You are a professional, gentle, and encouraging mental health analyst. 
Based on the following recent conversation history between the user and an AI therapist, provide a brief, insightful summary of the user's mental state.
Focus on:
1. Identifying their primary stressor or emotional pattern.
2. Highlighting any positive steps they've taken or strengths they've shown.
3. Offering one gentle piece of general advice.

Try to keep the response well-structured and easy to read. Do not act as the chatbot, act as an analyst providing a short report to the user.

Conversation History:
{history_text}"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://wellmind-ai.onrender.com",
            "X-OpenRouter-Title": "WellMindAI Insights"
        }
        
        payload = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "user", "content": insight_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 400
        }
        
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "Unable to generate insights at this time."
            
    except Exception as e:
        print(f"Insight error: {e}")
        return "Failed to analyze conversation history. Please try again later."