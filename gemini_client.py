import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def generer_contenu_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception(
            "Clé API Gemini introuvable. Vérifie le fichier .env ou la variable d'environnement GEMINI_API_KEY."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    texte = getattr(response, "text", None)
    if not texte:
        raise Exception("Réponse vide reçue depuis Gemini.")

    return texte