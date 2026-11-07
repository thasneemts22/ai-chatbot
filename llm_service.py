"""
LLM Service Layer for AI Chatbot.
Handles unified streaming communication with Google Gemini and Groq,
translating multi-turn conversation history, system personas, parameters, and multimodal inputs.
"""

import os
from typing import List, Dict, Any, Generator, Optional
import streamlit as st
from google import genai
from google.genai import types

try:
    import groq
except ImportError:
    groq = None


def get_secret(key_name: str) -> Optional[str]:
    """Retrieve secret from os.environ or streamlit secrets (for cloud hosting)."""
    val = os.environ.get(key_name)
    if not val:
        try:
            if hasattr(st, "secrets") and key_name in st.secrets:
                val = st.secrets[key_name]
        except Exception:
            pass
    return val


class LLMService:
    @staticmethod
    def stream_chat(
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_output_tokens: int = 4096,
        api_key: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime: Optional[str] = "image/png"
    ) -> Generator[str, None, None]:
        """
        Stream LLM responses token by token.
        
        Args:
            provider: 'Google Gemini' or 'Groq'
            model: Model name string (e.g. 'gemini-2.5-flash', 'llama-3.3-70b-versatile')
            messages: List of message dictionaries [{'role': 'user'|'assistant', 'content': '...'}]
            system_prompt: Optional system instruction/persona
            temperature: Generation temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            max_output_tokens: Maximum tokens in response
            api_key: API Key override (falls back to os.environ)
            image_bytes: Optional image attachment bytes for multimodal vision
            image_mime: MIME type of the attached image
        """
        if provider == "Google Gemini":
            yield from LLMService._stream_gemini(
                model=model,
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens,
                api_key=api_key,
                image_bytes=image_bytes,
                image_mime=image_mime
            )
        elif provider == "Groq":
            yield from LLMService._stream_groq(
                model=model,
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _stream_gemini(
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        temperature: float,
        top_p: float,
        max_output_tokens: int,
        api_key: Optional[str],
        image_bytes: Optional[bytes] = None,
        image_mime: Optional[str] = "image/png"
    ) -> Generator[str, None, None]:
        """Stream response using Google GenAI SDK (google-genai)."""
        key = api_key or get_secret("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "Gemini API Key is missing. Please add GEMINI_API_KEY to your .env file "
                "or enter it in the sidebar settings."
            )

        client = genai.Client(api_key=key)

        # Build conversation history in Google GenAI format
        contents: List[types.Content] = []

        for idx, msg in enumerate(messages):
            role = "user" if msg["role"] == "user" else "model"
            parts = []

            # Check if this is the latest user message with an attached image
            if idx == len(messages) - 1 and role == "user" and image_bytes:
                parts.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))

            # Add text part
            text_content = msg.get("content", "").strip()
            if text_content:
                parts.append(types.Part.from_text(text=text_content))

            if parts:
                contents.append(types.Content(role=role, parts=parts))

        # Generation configuration
        config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            system_instruction=system_prompt if system_prompt else None
        )

        # Candidate models with auto-fallback if one experiences a 503 high-demand spike
        candidate_models = [model]
        for fallback in ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None
        for candidate in candidate_models:
            try:
                response_stream = client.models.generate_content_stream(
                    model=candidate,
                    contents=contents,
                    config=config
                )
                has_yielded = False
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                        has_yielded = True
                if has_yielded:
                    return
            except Exception as e:
                err_msg = str(e)
                last_error = e
                # If high demand spike (503) or 404, try next candidate model in chain
                if any(k in err_msg for k in ["503", "UNAVAILABLE", "high demand", "404"]):
                    continue
                elif "RESOURCE_EXHAUSTED" in err_msg:
                    raise RuntimeError("API Rate limit reached. Please wait a moment before trying again.") from e
                elif "INVALID_ARGUMENT" in err_msg:
                    raise RuntimeError(f"Invalid API request or key: {err_msg}") from e
                elif "ConnectError" in err_msg or "getaddrinfo" in err_msg:
                    raise RuntimeError("Network connection failed. Please ensure your device has internet access.") from e
                else:
                    raise RuntimeError(f"Gemini API Error: {err_msg}") from e

        if last_error:
            raise RuntimeError(
                "Google Gemini servers are temporarily experiencing high demand across all free flash models. "
                "Please wait 10-20 seconds and click Retry."
            ) from last_error

    @staticmethod
    def _stream_groq(
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        temperature: float,
        max_output_tokens: int,
        api_key: Optional[str]
    ) -> Generator[str, None, None]:
        """Stream response using Groq Cloud API."""
        if groq is None:
            raise RuntimeError("The 'groq' package is not installed. Run: pip install groq")

        key = api_key or get_secret("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "Groq API Key is missing. Please add GROQ_API_KEY to your .env file "
                "or enter it in the sidebar settings."
            )

        client = groq.Groq(api_key=key)

        groq_messages = []
        if system_prompt:
            groq_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            groq_messages.append({"role": role, "content": msg.get("content", "")})

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            err_msg = str(e)
            if "rate_limit_exceeded" in err_msg:
                raise RuntimeError("Groq rate limit exceeded. Please wait a few seconds.") from e
            else:
                raise RuntimeError(f"Groq API Error: {err_msg}") from e
