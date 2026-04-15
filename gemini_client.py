import os
import tempfile


def _charger_env_projet():
    """Charge le .env du projet sans afficher la clé API."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    try:
        from dotenv import load_dotenv
    except ImportError:
        if not os.path.exists(env_path):
            return

        with open(env_path, "r", encoding="utf-8") as env_file:
            for ligne in env_file:
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#") or "=" not in ligne:
                    continue
                cle, valeur = ligne.split("=", 1)
                os.environ.setdefault(cle.strip(), valeur.strip().strip('"').strip("'"))
    else:
        load_dotenv(dotenv_path=env_path)


def _get_api_key() -> str:
    _charger_env_projet()
    return os.getenv("GEMINI_API_KEY", "").strip()


def _get_model_name() -> str:
    _charger_env_projet()
    return os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash").strip() or "gemini-2.5-flash"


_charger_env_projet()

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
    api_key = _get_api_key()
    model_name = _get_model_name()

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
        model = genai_legacy.GenerativeModel(model_name)
        response = model.generate_content(prompt)
    else:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

    texte = _extraire_texte_reponse(response)
    if not texte:
        raise Exception("Réponse vide reçue depuis Gemini.")

    return texte


def generer_contenu_gemini_stream(prompt: str, on_chunk=None) -> str:
    api_key = _get_api_key()
    model_name = _get_model_name()

    if not api_key:
        raise Exception(
            "Clé API Gemini introuvable. Vérifie le fichier .env ou la variable d'environnement GEMINI_API_KEY."
        )

    erreurs_sdk = []

    try:
        import google.generativeai as genai_legacy
    except ImportError as exc:
        erreurs_sdk.append(f"google-generativeai indisponible : {exc}")
    else:
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel(model_name)
        full_text = ""
        response_stream = model.generate_content(prompt, stream=True)

        for chunk in response_stream:
            try:
                chunk_text = _extraire_texte_reponse(chunk)
            except Exception:
                continue

            if not chunk_text:
                continue

            full_text += chunk_text
            if on_chunk:
                on_chunk(full_text)

        if full_text.strip():
            return full_text

    try:
        from google import genai
    except ImportError as exc:
        erreurs_sdk.append(f"google-genai indisponible : {exc}")
    else:
        client = genai.Client(api_key=api_key)
        full_text = ""

        if hasattr(client.models, "generate_content_stream"):
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=prompt
            )
            for chunk in response_stream:
                chunk_text = _extraire_texte_reponse(chunk)
                if not chunk_text:
                    continue

                full_text += chunk_text
                if on_chunk:
                    on_chunk(full_text)
        else:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            full_text = _extraire_texte_reponse(response)
            if on_chunk and full_text:
                on_chunk(full_text)

        if full_text.strip():
            return full_text

    detail = " | ".join(erreurs_sdk) if erreurs_sdk else "Réponse vide reçue depuis Gemini."
    raise Exception(f"Réponse vide reçue depuis Gemini. Détail : {detail}")


def generer_transcription_audio_gemini(
    audio_bytes: bytes,
    mime_type: str,
    file_name: str = "audio"
) -> str:
    api_key = _get_api_key()
    model_name = _get_model_name()

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
                model=model_name,
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
            model = genai_legacy.GenerativeModel(model_name)
            response = model.generate_content([prompt, uploaded_file])
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    texte = _extraire_texte_reponse(response)
    if not texte:
        raise Exception("Réponse vide reçue depuis Gemini pour la transcription audio.")

    return texte.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
