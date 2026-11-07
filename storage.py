"""
Session storage and persistence for AI Chatbot.
Saves conversations as JSON files in data/sessions, allowing users to revisit,
resume, export, or delete past chats just like in ChatGPT.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


def generate_title_from_prompt(prompt: str, max_words: int = 6) -> str:
    """Generate a clean, short session title from the first user prompt."""
    cleaned = prompt.strip().replace("\n", " ")
    words = cleaned.split()
    if not words:
        return "New Chat"
    title = " ".join(words[:max_words])
    if len(words) > max_words:
        title += "..."
    # Limit length
    return title[:45]


def create_new_session(
    provider: str = "Google Gemini",
    model: str = "gemini-3.8-flash",
    persona: str = "🤖 General Assistant",
    system_prompt: str = ""
) -> Dict[str, Any]:
    """Create a new empty session structure."""
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    session_data = {
        "id": session_id,
        "title": "New Chat",
        "created_at": now,
        "updated_at": now,
        "provider": provider,
        "model": model,
        "persona": persona,
        "system_prompt": system_prompt,
        "messages": []
    }
    save_session(session_data)
    return session_data


def get_session_file_path(session_id: str) -> str:
    """Get the JSON filepath for a session ID."""
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def save_session(session_data: Dict[str, Any]) -> None:
    """Save session data to a JSON file."""
    session_id = session_data.get("id")
    if not session_id:
        return
    session_data["updated_at"] = datetime.now().isoformat()
    filepath = get_session_file_path(session_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load a session by its ID."""
    filepath = get_session_file_path(session_id)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading session {session_id}: {e}")
        return None


def delete_session(session_id: str) -> bool:
    """Delete a session file."""
    filepath = get_session_file_path(session_id)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    return False


def list_sessions() -> List[Dict[str, Any]]:
    """List all saved sessions sorted by last updated timestamp (newest first)."""
    sessions = []
    if not os.path.exists(SESSIONS_DIR):
        return sessions

    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get("id"),
                        "title": data.get("title", "Untitled Chat"),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "message_count": len(data.get("messages", [])),
                        "model": data.get("model", ""),
                        "persona": data.get("persona", "")
                    })
            except Exception:
                continue

    # Sort newest first
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def export_as_markdown(session_data: Dict[str, Any]) -> str:
    """Format session into a readable Markdown document."""
    title = session_data.get("title", "Chat Transcript")
    created_at = session_data.get("created_at", "")
    model = session_data.get("model", "Unknown")
    persona = session_data.get("persona", "Default")
    
    lines = [
        f"# {title}",
        f"**Date:** {created_at}  ",
        f"**Model:** {model} | **Persona:** {persona}",
        "\n---\n"
    ]

    for msg in session_data.get("messages", []):
        role = "🧑 User" if msg["role"] == "user" else "🤖 Assistant"
        time_str = msg.get("timestamp", "")
        lines.append(f"### {role} ({time_str})\n")
        lines.append(msg.get("content", ""))
        lines.append("\n---\n")

    return "\n".join(lines)
