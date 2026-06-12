import requests
from config.ai_config import OLLAMA_API_URL, DEFAULT_OLLAMA_MODEL


def generate(prompt: str) -> str:
    """
    Generate response using local Ollama model.
    """
    payload = {"model": DEFAULT_OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.Timeout:
        return "Error: Local Ollama request timed out (30 seconds limit). Please ensure your local Ollama server is responding."
    except requests.exceptions.ConnectionError:
        return (
            "Error: Could not connect to local Ollama server. "
            "Please ensure Ollama is installed and running (`ollama serve`), and you have pulled the model (`ollama pull llama3`)."
        )
    except Exception as e:
        return f"Error: An unexpected error occurred while communicating with Ollama: {str(e)}"
