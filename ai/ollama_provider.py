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
        return (
            "⚠️ **Local Ollama request timed out (30 seconds limit).**\n\n"
            "Please ensure your local Ollama server is responding and not overloaded."
        )
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ **Could not connect to local Ollama server.**\n\n"
            "This error usually happens for one of two reasons:\n\n"
            "1. **You are using the deployed Streamlit Cloud website**: The cloud server cannot access your local computer's `localhost`. "
            "To use Ollama, you must clone this project and run the app locally on your machine (`streamlit run app.py`). "
            "Alternatively, switch to **Gemini (BYOK)** in the sidebar to run the app in the cloud.\n"
            "2. **Ollama is not running locally**: If you are already running the app locally, please ensure the Ollama app is open and running on your Mac (or run `ollama serve` in your terminal), and that you have pulled the model by running `ollama pull llama3` in your terminal."
        )
    except Exception as e:
        return f"Error: An unexpected error occurred while communicating with Ollama: {str(e)}"
