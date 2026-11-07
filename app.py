"""
ChatGPT Clone - Python & LLM AI Chatbot Web Application
Built with Streamlit, Google GenAI SDK (Gemini), Groq, and persistent session storage.
"""

import os
import sys
import time
from datetime import datetime
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Windows console UTF-8 fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import config
import storage
from llm_service import LLMService

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ChatGPT AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT Aesthetic
st.markdown("""
<style>
    /* Sleek container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }
    
    /* Welcome Hero Header */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #4A90E2, #9013FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        text-align: center;
        color: #888888;
        margin-bottom: 2rem;
    }
    
    /* Starter Prompt Cards */
    .starter-card {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 14px 18px;
        cursor: pointer;
        transition: transform 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
        min-height: 80px;
    }
    .starter-card:hover {
        transform: translateY(-2px);
        border-color: #4A90E2;
        background-color: rgba(74, 144, 226, 0.08);
    }
    .starter-card-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }
    .starter-card-sub {
        font-size: 0.82rem;
        color: #888888;
    }
    
    /* Meta tags & badges */
    .chat-meta {
        font-size: 0.75rem;
        color: #888888;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "current_session_id" not in st.session_state:
    all_sessions = storage.list_sessions()
    if all_sessions:
        st.session_state.current_session_id = all_sessions[0]["id"]
    else:
        new_sess = storage.create_new_session()
        st.session_state.current_session_id = new_sess["id"]

# Load current session data
current_session = storage.load_session(st.session_state.current_session_id)
if not current_session:
    current_session = storage.create_new_session()
    st.session_state.current_session_id = current_session["id"]


# -----------------------------------------------------------------------------
# Sidebar: ChatGPT Controls & History
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🤖 AI Chatbot")
    
    # + New Chat Button
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        new_sess = storage.create_new_session(
            provider=current_session.get("provider", "Google Gemini"),
            model=current_session.get("model", "gemini-3.5-flash-lite"),
            persona=current_session.get("persona", "🤖 General Assistant"),
            system_prompt=current_session.get("system_prompt", "")
        )
        st.session_state.current_session_id = new_sess["id"]
        st.rerun()

    st.markdown("---")

    # Automated Settings (Optimized for speed)
    selected_provider = "Google Gemini"
    selected_model = "gemini-3.5-flash-lite"
    temperature = config.DEFAULT_TEMPERATURE
    max_tokens = config.DEFAULT_MAX_TOKENS
    custom_api_key = None

    # Conversation History List
    st.subheader("💬 Chat History")
    all_sessions = storage.list_sessions()
    
    if all_sessions:
        for s in all_sessions:
            s_id = s["id"]
            is_active = (s_id == st.session_state.current_session_id)
            title = s["title"]
            msg_count = s["message_count"]
            label = f"{'🟢 ' if is_active else '💬 '}{title} ({msg_count})"

            cols = st.columns([0.82, 0.18])
            with cols[0]:
                if st.button(label, key=f"sess_{s_id}", use_container_width=True, type="secondary" if not is_active else "primary"):
                    st.session_state.current_session_id = s_id
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"del_{s_id}", help="Delete chat"):
                    storage.delete_session(s_id)
                    remaining = storage.list_sessions()
                    if remaining:
                        st.session_state.current_session_id = remaining[0]["id"]
                    else:
                        new_s = storage.create_new_session()
                        st.session_state.current_session_id = new_s["id"]
                    st.rerun()
    else:
        st.caption("No saved chats yet.")

    # Export Section
    st.markdown("---")
    st.subheader("📥 Export Chat")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        md_data = storage.export_as_markdown(current_session)
        st.download_button(
            "📄 Markdown",
            data=md_data,
            file_name=f"chat_{current_session['title'][:20].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with exp_col2:
        import json
        json_data = json.dumps(current_session, indent=2, ensure_ascii=False)
        st.download_button(
            "📦 JSON",
            data=json_data,
            file_name=f"chat_{current_session['title'][:20].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )


# -----------------------------------------------------------------------------
# Main Chat Area
# -----------------------------------------------------------------------------
head_col1, head_col2 = st.columns([0.68, 0.32])
with head_col1:
    st.title(current_session.get("title", "New Chat"))

persona_names = list(config.PERSONAS.keys())
current_persona = current_session.get("persona", persona_names[0])
with head_col2:
    selected_persona = st.selectbox(
        "AI Mode",
        options=persona_names,
        index=persona_names.index(current_persona) if current_persona in persona_names else 0,
        label_visibility="collapsed",
        key="top_persona_selector",
        help="Switch AI Persona (e.g. Coding, Tutor, Storyteller)"
    )

if selected_persona == "🛠️ Custom System Prompt":
    custom_prompt = st.text_input(
        "Enter custom instructions:",
        value=current_session.get("system_prompt", ""),
        placeholder="e.g. You are a senior Python specialist...",
        label_visibility="collapsed"
    )
else:
    custom_prompt = config.PERSONAS[selected_persona]

# Update session persona if changed
if (current_session.get("persona") != selected_persona or
    current_session.get("system_prompt") != custom_prompt):
    current_session["persona"] = selected_persona
    current_session["system_prompt"] = custom_prompt
    storage.save_session(current_session)

# Welcome / Empty State
messages = current_session.get("messages", [])
pending_prompt = None

if len(messages) == 0:
    st.markdown('<div class="hero-title">What can I help with today?</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Ask questions, generate code, brainstorm ideas, or analyze text.</div>', unsafe_allow_html=True)

    # 2x2 Grid of Starter Prompt Cards
    col1, col2 = st.columns(2)
    with col1:
        card1 = config.STARTER_PROMPTS[0]
        if st.button(f"{card1['icon']} **{card1['title']}**\n\n{card1['subtitle']}", key="starter_0", use_container_width=True):
            pending_prompt = card1["prompt"]

        card3 = config.STARTER_PROMPTS[2]
        if st.button(f"{card3['icon']} **{card3['title']}**\n\n{card3['subtitle']}", key="starter_2", use_container_width=True):
            pending_prompt = card3["prompt"]

    with col2:
        card2 = config.STARTER_PROMPTS[1]
        if st.button(f"{card2['icon']} **{card2['title']}**\n\n{card2['subtitle']}", key="starter_1", use_container_width=True):
            pending_prompt = card2["prompt"]

        card4 = config.STARTER_PROMPTS[3]
        if st.button(f"{card4['icon']} **{card4['title']}**\n\n{card4['subtitle']}", key="starter_3", use_container_width=True):
            pending_prompt = card4["prompt"]

# Render Existing Messages
for msg in messages:
    role = msg["role"]
    avatar = "🧑" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.get("content", ""))
        if "meta" in msg:
            st.markdown(f"<div class='chat-meta'>{msg['meta']}</div>", unsafe_allow_html=True)

# User Chat Input with NATIVE file/image upload button directly INSIDE the input box!
user_input_val = st.chat_input(
    "Message ChatGPT...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "webp"]
)

# Parse text and attached image
prompt_text = None
attached_image_bytes = None
attached_image_mime = None

if pending_prompt:
    prompt_text = pending_prompt
elif user_input_val:
    if hasattr(user_input_val, "text"):
        prompt_text = (user_input_val.text or "").strip()
        files = getattr(user_input_val, "files", []) or []
        if files:
            try:
                attached_image_bytes = files[0].getvalue()
                attached_image_mime = files[0].type
            except Exception:
                pass
    elif isinstance(user_input_val, str):
        prompt_text = user_input_val.strip()

if prompt_text or attached_image_bytes:
    final_prompt = prompt_text if prompt_text else ("What is in this image?" if attached_image_bytes else "Hello")

    # 1. Update session title if first message
    if len(messages) == 0:
        new_title = storage.generate_title_from_prompt(final_prompt)
        current_session["title"] = new_title

    # 2. Add user message
    now_str = datetime.now().strftime("%I:%M %p")
    user_msg = {
        "role": "user",
        "content": final_prompt,
        "timestamp": now_str
    }
    current_session["messages"].append(user_msg)
    storage.save_session(current_session)

    # Render User Message immediately
    with st.chat_message("user", avatar="🧑"):
        if attached_image_bytes:
            try:
                st.image(attached_image_bytes, width=280)
            except Exception:
                pass
        st.markdown(final_prompt)

    # 3. Stream Assistant Response
    with st.chat_message("assistant", avatar="🤖"):
        start_time = time.time()
        try:
            effective_key = custom_api_key.strip() if custom_api_key else None
            
            with st.spinner("🤖 Thinking..."):
                stream_gen = LLMService.stream_chat(
                    provider=selected_provider,
                    model=selected_model,
                    messages=current_session["messages"],
                    system_prompt=custom_prompt,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    api_key=effective_key,
                    image_bytes=attached_image_bytes,
                    image_mime=attached_image_mime
                )

                # Live streaming response
                full_response = st.write_stream(stream_gen)
            elapsed = time.time() - start_time
            meta_info = f"⚡ Generated with {selected_model} in {elapsed:.2f}s"

            # 4. Save assistant response
            assistant_msg = {
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "meta": meta_info
            }
            current_session["messages"].append(assistant_msg)
            storage.save_session(current_session)
            
            # Rerun on success to update session history and UI
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating response: {e}")
            # Remove failed turn from messages so session is not corrupted
            if current_session["messages"] and current_session["messages"][-1]["role"] == "user":
                current_session["messages"].pop()
                storage.save_session(current_session)
