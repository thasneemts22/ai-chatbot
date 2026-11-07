"""
Configuration settings for AI Chatbot (ChatGPT Clone).
Defines supported models, system personas, default parameters, and starter prompt ideas.
"""

# Available LLM Providers & Models
PROVIDERS = {
    "Google Gemini": {
        "models": [
            {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash (Fast & Smart - Recommended)"},
            {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash"},
            {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash"},
            {"id": "gemini-3.1-flash-lite", "name": "Gemini 3.1 Flash Lite (Ultra Fast)"},
            {"id": "gemini-flash-latest", "name": "Gemini Flash Latest"},
        ],
        "env_var": "GEMINI_API_KEY",
        "description": "Google's state-of-the-art multimodal model with streaming & high speed."
    },
    "Groq": {
        "models": [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile (Meta - Blazing Fast)"},
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant"},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B (32k context)"},
        ],
        "env_var": "GROQ_API_KEY",
        "description": "Ultra-fast LPU inference engine for open-source open-weights models."
    }
}

# Pre-defined Personas / System Instructions
PERSONAS = {
    "🤖 General Assistant": (
        "You are a helpful, harmless, and honest AI assistant, modeled after ChatGPT. "
        "You provide well-structured, polite, and insightful responses. "
        "Format your output with clean Markdown, bullet points, and code blocks with language tags when appropriate."
    ),
    "💻 Senior Software Engineer": (
        "You are an expert Senior Full-Stack Software Architect and Polyglot Developer. "
        "Provide production-ready, clean, well-commented, and robust code. "
        "Point out potential edge cases, time/space complexity, performance pitfalls, and best practices. "
        "Always use appropriate code fence tags."
    ),
    "🎓 Patient Tutor & Teacher": (
        "You are an encouraging and deeply knowledgeable educator. "
        "You explain complex topics using the Feynman technique: intuitive real-world analogies, "
        "step-by-step breakdowns, and practical examples before diving into formal definitions. "
        "Encourage questions and test understanding gently."
    ),
    "✍️ Creative Writer & Storyteller": (
        "You are a master storyteller, copywriter, and creative stylist. "
        "Write with evocative imagery, vibrant rhythm, compelling hooks, and emotional resonance. "
        "Adapt your tone seamlessly between poetic, cinematic, journalistic, or conversational."
    ),
    "⚡ Ultra-Concise & Bullet Points": (
        "You are a direct, zero-fluff assistant. Provide immediate, high-density answers strictly in bullet points. "
        "No conversational filler, no pleasantries, no repetitive conclusions. Just the core facts and actions."
    ),
    "🕵️ Code & Logic Debugger": (
        "You specialize in tracking down bugs, architectural bottlenecks, and logic errors. "
        "When given code or a problem, diagnose root causes first, explain why the bug occurred, "
        "and then provide the minimal correct fix followed by defensive programming tips."
    ),
    "🛠️ Custom System Prompt": ""
}

# ChatGPT-style Quick Starter Prompt Cards
STARTER_PROMPTS = [
    {
        "icon": "💡",
        "title": "Explain a complex concept",
        "subtitle": "Quantum computing in simple words",
        "prompt": "Explain Quantum Computing and superposition to a curious 12-year-old using everyday analogies."
    },
    {
        "icon": "🐍",
        "title": "Python Architecture",
        "subtitle": "Build a modular FastAPI service",
        "prompt": "Design a clean folder structure and starter code for a production FastAPI REST API with authentication and SQLite."
    },
    {
        "icon": "✍️",
        "title": "Draft an email",
        "subtitle": "Professional project delay update",
        "prompt": "Draft a polite and professional email to a client explaining a 1-week timeline push due to security testing."
    },
    {
        "icon": "🚀",
        "title": "Brainstorm Startup Ideas",
        "subtitle": "AI-powered developer productivity tools",
        "prompt": "Give me 5 innovative SaaS product ideas that solve real developer pain points using modern LLM agents."
    }
]

# Generation Parameter Defaults
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_MAX_TOKENS = 4096
