import google.generativeai as genai

API_KEY = "PASTE_YOUR_GEMINI_KEY"

genai.configure(api_key=API_KEY)

for model in genai.list_models():
    print(model.name)
