import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: No API Key found.")
else:
    genai.configure(api_key=api_key)
    print("--- MODELOS DISPONIBLES PARA TU API KEY ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Nombre: {m.name}")
    except Exception as e:
        print(f"Error listando modelos: {e}")