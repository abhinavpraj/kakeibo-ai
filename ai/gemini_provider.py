import google.generativeai as genai
from config.ai_config import DEFAULT_GEMINI_MODEL


def generate(prompt: str, api_key: str) -> str:
    """
    Generate response using Google Gemini BYOK.
    """
    if not api_key or not api_key.strip():
        return "Error: Gemini API Key is missing. Please enter your API Key in the '🤖 AI Settings' sidebar panel."

    try:
        genai.configure(api_key=api_key.strip())
        model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
        response = model.generate_content(prompt)
        if not response or not hasattr(response, "text"):
            return "Error: Empty or invalid response returned from Gemini API."
        return response.text
    except Exception as e:
        err_msg = str(e)
        if (
            "API_KEY_INVALID" in err_msg
            or "API key not valid" in err_msg
            or "invalid" in err_msg.lower()
        ):
            return "Error: The provided Gemini API Key is invalid. Please double-check your API Key in the sidebar."
        return f"Error: Gemini API invocation failed: {err_msg}"
