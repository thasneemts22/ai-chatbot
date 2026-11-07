# 🤖 AI Chatbot (ChatGPT Clone) - Python & LLM

A fully-featured, production-ready AI Chatbot application built using **Python**, **Streamlit**, and state-of-the-art LLMs (**Google Gemini** & **Groq**). It replicates the core features of ChatGPT with a clean user interface, real-time token streaming, session history persistence, personas, and multimodal image analysis.

---

## ✨ Features

- **⚡ Real-time Token Streaming**: Responses appear word-by-word just like ChatGPT via `st.write_stream`.
- **💬 Chat History & Persistence**:
  - Automatically saves all conversations to disk in `data/sessions/`.
  - Re-visit, rename, or delete past conversations from the sidebar anytime.
- **🎭 System Personas & Custom Instructions**:
  - 🤖 General Assistant (ChatGPT style)
  - 💻 Senior Software Engineer
  - 🎓 Patient Tutor (Feynman technique)
  - ✍️ Creative Writer & Copywriter
  - ⚡ Ultra-Concise & Bullet Points
  - 🕵️ Code & Logic Debugger
  - 🛠️ Custom Prompt (Write your own instructions!)
- **🔄 Multi-Provider & Model Switching**:
  - **Google Gemini**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`
  - **Groq**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`
- **🖼️ Multimodal Vision**: Upload images (PNG, JPG, WEBP) and ask the AI to analyze, explain, or code based on them.
- **📥 Export Conversations**: Export chat history to **Markdown (`.md`)** or **JSON (`.json`)** with a single click.
- **💡 Starter Prompt Cards**: Interactive prompt suggestion cards on new chats to start conversations instantly.
- **🎛️ Hyperparameter Tuning**: Adjust Temperature (creativity) and Max Output Tokens directly in the sidebar.

---

## 📁 Project Architecture

```
ai_chatbot/
│
├── app.py                 # Main Streamlit web application & UI
├── config.py              # Models, system personas, and starter prompts
├── storage.py             # Session persistence & JSON/Markdown export
├── llm_service.py         # Unified LLM streaming engine (Gemini & Groq)
├── requirements.txt       # Python dependencies
├── .env                   # API keys configuration (GEMINI_API_KEY, GROQ_API_KEY)
├── .env.example           # Template for environment variables
├── run.bat                # Windows 1-click launch script
└── data/
    └── sessions/          # Automatically saved chat conversations (JSON)
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
cd ai_chatbot
pip install -r requirements.txt
```

### 3. Configure API Key
Create or verify your `.env` file in `ai_chatbot/`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```
> **Tip:** You can obtain a free Gemini API key at [Google AI Studio](https://aistudio.google.com/).

### 4. Run the Application
You can run it directly:
```bash
streamlit run app.py
```
Or double-click `run.bat` on Windows!

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧠 How It Works (Concepts)

1. **Context Window & Chat Memory**:
   - LLMs are stateless by default. To make them remember earlier messages, the full sequence of turns (`user` and `model` / `assistant`) is sent to the LLM on every new prompt.
2. **Streaming**:
   - Instead of waiting 5–10 seconds for the complete answer, `generate_content_stream` yields tokens as they are produced by the neural network, creating the interactive ChatGPT typing effect.
3. **System Instructions / Personas**:
   - The persona string sets the behavioral guidelines, tone, and formatting constraints for the model before any user input is processed.
