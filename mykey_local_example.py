"""
Example mykey configuration for local LLM via Ollama or LM Studio.

Copy this file to mykey.py and adjust the values as needed. This example assumes a local model running on http://localhost:11434.
"""

# Configuration for a local OpenAI-compatible provider using Ollama or LM Studio.
oai_local_ollama = {
    "apikey": "ollama",  # placeholder; local providers typically do not require a real API key
    "apibase": "http://127.0.0.1:11434",
    "model": "gemma4:latest",  # change to the model name you have available locally
    "api_mode": "chat_completions",
    "stream": True,
}
