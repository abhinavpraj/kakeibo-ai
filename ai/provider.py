from typing import Optional
from ai.ollama_provider import generate as ollama_generate
from ai.gemini_provider import generate as gemini_generate


def ask_ai(provider: str, prompt: str, api_key: Optional[str] = None) -> str:
    """
    Route prompt generation to the configured AI provider.
    """
    if provider == "Ollama":
        return ollama_generate(prompt)
    elif provider == "Gemini":
        return gemini_generate(prompt, api_key or "")
    else:
        return f"Error: Unknown or unsupported AI provider '{provider}'."
