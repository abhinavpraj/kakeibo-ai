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

        # Dynamically discover the best available model supporting generateContent
        model_name = DEFAULT_GEMINI_MODEL
        try:
            available_models = list(genai.list_models())
            supported_models = [m.name for m in available_models if "generateContent" in m.supported_generation_methods]
            # Clean names (remove prefix like 'models/')
            clean_names = [m.replace("models/", "") for m in supported_models]

            # Check if default model (gemini-1.5-flash) is directly supported
            if DEFAULT_GEMINI_MODEL in clean_names:
                model_name = DEFAULT_GEMINI_MODEL
            else:
                # Priority: newer or different flash models
                priorities = [
                    "gemini-2.5-flash",
                    "gemini-3.5-flash",
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                ]
                matched = False
                for p in priorities:
                    if p in clean_names:
                        model_name = p
                        matched = True
                        break

                if not matched:
                    # Look for any model with 'flash'
                    flash_models = [m for m in clean_names if "flash" in m]
                    if flash_models:
                        model_name = flash_models[0]
                    else:
                        # Look for any 'pro' models
                        pro_models = [m for m in clean_names if "pro" in m]
                        if pro_models:
                            model_name = pro_models[0]
                        elif clean_names:
                            # Default to the first available model that supports generation
                            model_name = clean_names[0]
        except Exception:  # nosec B110
            # If list_models fails (e.g. permission/network issue), fallback to the config default
            pass

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        if not response or not hasattr(response, "text"):
            return "Error: Empty or invalid response returned from Gemini API."
        return response.text
    except Exception as e:
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg or "invalid" in err_msg.lower():
            return "Error: The provided Gemini API Key is invalid. Please double-check your API Key in the sidebar."
        return f"Error: Gemini API invocation failed: {err_msg}"
