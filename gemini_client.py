import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

def _extraire_texte_reponse(response) -> str:
    texte = getattr(response, "text", None)
    if texte:
        return texte

    morceaux = []
    for candidat in getattr(response, "candidates", []) or []:
        contenu = getattr(candidat, "content", None)
        for part in getattr(contenu, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                morceaux.append(part_text)

    return "\n".join(morceaux).strip()


def generer_contenu_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception(
            "Clé API Gemini introuvable. Vérifie le fichier .env ou la variable d'environnement GEMINI_API_KEY."
        )

    response = None
    try:
        from google import genai
    except ImportError:
        try:
            import google.generativeai as genai_legacy
        except ImportError as exc:
            raise Exception(
                "Aucun SDK Gemini compatible n'est installe. Installez google-generativeai ou google-genai."
            ) from exc

        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
    else:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    texte = _extraire_texte_reponse(response)
    if not texte:
        raise Exception("Réponse vide reçue depuis Gemini.")

    return texte


def generer_transcription_audio_gemini(
    audio_bytes: bytes,
    mime_type: str,
    file_name: str = "audio"
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception(
            "Clé API Gemini introuvable. Vérifie le fichier .env ou la variable d'environnement GEMINI_API_KEY."
        )

    prompt = (
        "Tu es un moteur de transcription audio forensique. "
        "Transcris fidèlement l'enregistrement fourni. "
        "Ne résume pas. Ne traduis pas. "
        "Conserve les hésitations, chiffres, noms propres et termes ambigus autant que possible. "
        "Si un passage est inaudible, écris [inaudible]. "
        "Retourne uniquement la transcription brute, sans introduction ni commentaire."
    )

    response = None
    modern_error = None
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        modern_error = None
    else:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                ]
            )
        except Exception as exc:
            modern_error = exc

    if response is None:
        try:
            import google.generativeai as genai_legacy
        except ImportError as exc:
            if modern_error is not None:
                raise Exception(
                    f"Echec de transcription audio avec le SDK Gemini moderne : {modern_error}"
                ) from modern_error
            raise Exception(
                "Aucun SDK Gemini compatible n'est installe. Installez google-generativeai ou google-genai."
            ) from exc

        temp_path = None
        try:
            suffix = os.path.splitext(file_name)[1] or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                temp_path = tmp.name

            genai_legacy.configure(api_key=api_key)
            uploaded_file = genai_legacy.upload_file(
                path=temp_path,
                mime_type=mime_type,
                display_name=file_name
            )
            model = genai_legacy.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([prompt, uploaded_file])
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    texte = _extraire_texte_reponse(response)
    if not texte:
        raise Exception("Réponse vide reçue depuis Gemini pour la transcription audio.")

    return texte.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
