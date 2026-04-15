"""
Module Pièce E : Mobile Data - Analyse WhatsApp IA/NLP
Analyste : Ahmed dany
Date : Février 2026
Affaire : TechCorp - Fuite de données Projet Orion

"""
import os
import sqlite3
import json
import hashlib
from datetime import datetime
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

def _charger_env_mobile():
    """Charge le fichier .env du projet pour le module Mobile uniquement."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    try:
        from dotenv import load_dotenv
    except ImportError:
        if not os.path.exists(env_path):
            return

        # Fallback minimal si python-dotenv n'est pas disponible dans l'env actif.
        with open(env_path, "r", encoding="utf-8") as env_file:
            for ligne in env_file:
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#") or "=" not in ligne:
                    continue
                cle, valeur = ligne.split("=", 1)
                cle = cle.strip()
                valeur = valeur.strip().strip('"').strip("'")
                os.environ.setdefault(cle, valeur)
    else:
        load_dotenv(dotenv_path=env_path)


_charger_env_mobile()

# Patterns suspects pour la détection NLP
PATTERNS_SUSPECTS = {
    'culinaire': {
        'mots': ['gâteau', 'four', 'recette', 'ingrédients', 'cuisiner', 'cuire', 'pâtisserie'],
        'points': 3,
        'niveau': 'ÉLEVÉ'
    },
    'livraison': {
        'mots': ['colis', 'paquet', 'livraison', 'marchandise', 'envoyer', 'expédition', 'canal'],
        'points': 3,
        'niveau': 'ÉLEVÉ'
    },
    'vague': {
        'mots': ['chose', 'détails', 'élément', 'matériel', 'affaire', 'dossier', 'ressources'],
        'points': 1.5,
        'niveau': 'MOYEN'
    },
    'confidentialite': {
        'mots': ['discret', 'secret', 'entre nous', 'privé', 'habituel', 'personnel', 'strictement'],
        'points': 3,
        'niveau': 'ÉLEVÉ'
    },
    'financier': {
        'mots': ['paiement', 'compensation', 'arrangement', 'récompense', 'transaction', 'salaire'],
        'points': 1.5,
        'niveau': 'MOYEN'
    }
}

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "tiny")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")


def _get_gemini_api_key_mobile():
    _charger_env_mobile()
    return os.getenv("GEMINI_API_KEY")


def _extraire_texte_reponse_gemini(response):
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


def _generer_contenu_gemini_mobile(prompt, on_chunk=None):
    """Genere le rapport via Gemini Flash avec streaming quand le SDK le permet."""
    api_key = _get_gemini_api_key_mobile()
    if not api_key:
        raise RuntimeError(
            "Clé API Gemini introuvable. Ajoutez GEMINI_API_KEY dans le fichier .env du projet."
        )

    erreurs_sdk = []

    try:
        import google.generativeai as genai_legacy
    except ImportError as exc:
        erreurs_sdk.append(f"google-generativeai indisponible : {exc}")
    else:
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel(GEMINI_MODEL_NAME)
        full_report = ""
        response_stream = model.generate_content(prompt, stream=True)

        for chunk in response_stream:
            try:
                chunk_text = _extraire_texte_reponse_gemini(chunk)
            except Exception:
                continue

            if not chunk_text:
                continue

            full_report += chunk_text
            if on_chunk:
                on_chunk(full_report)

        if full_report.strip():
            return full_report

    try:
        from google import genai
    except ImportError as exc:
        erreurs_sdk.append(f"google-genai indisponible : {exc}")
    else:
        client = genai.Client(api_key=api_key)
        full_report = ""

        if hasattr(client.models, "generate_content_stream"):
            response_stream = client.models.generate_content_stream(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            for chunk in response_stream:
                chunk_text = _extraire_texte_reponse_gemini(chunk)
                if not chunk_text:
                    continue

                full_report += chunk_text
                if on_chunk:
                    on_chunk(full_report)
        else:
            response = client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            full_report = _extraire_texte_reponse_gemini(response)
            if on_chunk and full_report:
                on_chunk(full_report)

        if full_report.strip():
            return full_report

    detail = " | ".join(erreurs_sdk) if erreurs_sdk else "Réponse vide reçue depuis Gemini."
    raise RuntimeError(
        "Impossible de générer le rapport avec Gemini Flash. "
        f"Détail : {detail}"
    )

def _normaliser_texte_pdf(texte):
    """Nettoie le texte pour rester compatible avec FPDF latin-1."""
    remplacements = {
        'œ': 'oe',
        'Œ': 'OE',
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        '–': '-',
        '—': '-',
        '…': '...',
        '→': '->',
        '•': '-',
        '\u00a0': ' ',
        '🔴': '[Critique]',
        '🟠': '[Eleve]',
        '🟡': '[Moyen]',
        '🟢': '[Faible]',
        '✅': '[OK]',
        '⚠️': '[Attention]',
        '📝': '[Rapport]',
        '📱': '[Mobile]',
        '🎙️': '[Audio]',
        '🤖': '[IA]',
        '🏛️': '[DFIR]',
    }

    texte_normalise = texte or ""
    for caractere, remplacement in remplacements.items():
        texte_normalise = texte_normalise.replace(caractere, remplacement)

    return texte_normalise


def generate_pdf_report(texte_md):
    """Genere un PDF robuste a partir du rapport Markdown."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError(
            "La bibliotheque fpdf n'est pas installee. Installez-la avec : pip install fpdf"
        ) from exc

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, "RAPPORT D'EXPERTISE FORENSIQUE - POLE MOBILE", 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title("Rapport Expertise Mobile")

    texte_normalise = _normaliser_texte_pdf(texte_md)

    for ligne in texte_normalise.splitlines():
        ligne = ligne.strip()

        if not ligne:
            pdf.ln(4)
            continue

        if ligne.startswith('#'):
            titre = ligne.replace('#', '').replace('*', '').strip().upper()
            pdf.set_font("Arial", 'B', 12)
            safe_title = titre.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, txt=safe_title)
            pdf.ln(2)
            continue

        contenu = ligne.replace('**', '').replace('*', '-').replace('`', '')
        pdf.set_font("Arial", size=11)
        safe_line = contenu.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 6, txt=safe_line)

    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, bytes):
        return pdf_output
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')

    return bytes(pdf_output)


def _whisper_cache_dir():
    return os.getenv(
        "WHISPER_DOWNLOAD_ROOT",
        os.path.join(os.path.expanduser("~"), ".cache", "whisper")
    )


def _whisper_model_cache_path(model_name=WHISPER_MODEL_NAME):
    try:
        import whisper
    except ImportError:
        return None

    model_url = whisper._MODELS.get(model_name)
    if not model_url:
        return None

    return os.path.join(_whisper_cache_dir(), os.path.basename(model_url))


def _whisper_model_cached(model_name=WHISPER_MODEL_NAME):
    model_path = _whisper_model_cache_path(model_name)
    return bool(model_path and os.path.exists(model_path))


def _commande_prechargement_whisper():
    cache_dir = _whisper_cache_dir()
    return (
        f"python3 -c \"import whisper; whisper.load_model('{WHISPER_MODEL_NAME}', "
        f"download_root=r'{cache_dir}')\""
    )
# ═══════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

def run():
    """Fonction principale du module Mobile NLP"""
    


    # 1. En-tête de la page
    st.markdown("## 📱 Pôle d'Analyse : Mobile Data - Analyse WhatsApp IA/NLP")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.info("🧑‍💻 **Analyste DFIR :** Ahmed")
    col_b.info("🎯 **Cible :** `mobile_Employe` (Jean Martin)")
    col_c.info("🛠️ **Outils :** NLP + ASR (Whisper)")
    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Messages Texte", 
        "🎙️ Notes Vocales", 
        "📊 Résultats Globaux",
        "🔐 Conformité Forensique",
        "📝 Rapport "
    ])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1 : ANALYSE MESSAGES TEXTE
    # ═══════════════════════════════════════════════════════════════
    
    with tab1:
        st.header("📝 Analyse NLP - Messages Texte WhatsApp")
        
        st.subheader("1️⃣ Upload de la base de données")
        db_file = st.file_uploader(
            "Sélectionnez le fichier msgstore.db",
            type=['db'],
            help="Base de données SQLite extraite de WhatsApp",
            key="db_upload"
        )
        
        if db_file:
            st.success("✅ Fichier chargé : " + db_file.name)
            
            if st.button("🚀 Analyser les messages", key="analyze_text"):
                with st.spinner("Analyse NLP en cours..."):
                    try:
                        results = analyser_messages_whatsapp(db_file)
                        st.session_state['text_results'] = results
                        st.success("✅ Analyse terminée !")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
            
            if 'text_results' in st.session_state:
                afficher_resultats_texte(st.session_state['text_results'])
        else:
            st.warning("⚠️ Veuillez uploader un fichier msgstore.db pour commencer")
        st.session_state['db_file'] = db_file
    # ═══════════════════════════════════════════════════════════════
    # TAB 2 : ANALYSE NOTES VOCALES (WHISPER DYNAMIQUE)
    # ═══════════════════════════════════════════════════════════════
    
    with tab2:
        st.header("🎙️ Analyse ASR - Notes Vocales WhatsApp")
        
        st.subheader("1️⃣ Upload des notes vocales")
        audio_files = st.file_uploader(
            "Sélectionnez les fichiers audio (.opus, .ogg, .m4a)",
            type=['opus', 'ogg', 'm4a'],
            accept_multiple_files=True,
            help="Notes vocales extraites de WhatsApp",
            key="audio_upload"
        )
        
        if audio_files:
            st.success(f"✅ {len(audio_files)} fichiers audio chargés")
            
            # Info sur Whisper
            st.info("""
            🎙️ **Transcription avec Whisper (OpenAI)**
            
            - Moteur : `Whisper {}` uniquement
            - Exécution : CPU local
            - Temps estimé : ~30-60 secondes par fichier
            - Précision attendue : ~70-75% (français)
            
            ⏱️ **Temps total estimé :** {:.1f} minutes
            
            💡 **Astuce :** au premier lancement, Whisper peut devoir télécharger son modèle une seule fois dans le cache local.
            """.format(WHISPER_MODEL_NAME, len(audio_files) * 0.5))
            
            if st.button("🚀 Transcrire et Analyser avec Whisper", key="analyze_audio"):
                with st.spinner(f"Transcription de {len(audio_files)} fichiers avec Whisper..."):
                    try:
                        st.session_state['audio_results'] = []
                        results = transcrire_et_analyser_whisper(audio_files)
                        if results:
                            st.session_state['audio_results'] = results
                            st.success("✅ Transcription et analyse terminées !")
                        else:
                            st.warning("⚠️ Aucun fichier audio n'a pu être transcrit.")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la transcription : {str(e)}")
                        st.info("💡 Whisper uniquement est activé. Vérifiez le cache local du modèle ou la connexion nécessaire pour le premier téléchargement.")
                        st.code(_commande_prechargement_whisper(), language="bash")
            
            if 'audio_results' in st.session_state:
                afficher_resultats_audio(st.session_state['audio_results'])
        else:
            st.warning("⚠️ Veuillez uploader des fichiers audio pour commencer")
        st.session_state['audio_files'] = audio_files
    # ═══════════════════════════════════════════════════════════════
    # TAB 3 : RÉSULTATS GLOBAUX
    # ═══════════════════════════════════════════════════════════════
    
    with tab3:
        st.header("📊 Résultats Globaux - Vue d'Ensemble")
        
        if 'text_results' in st.session_state or 'audio_results' in st.session_state:
            afficher_vue_globale()
        else:
            st.info("ℹ️ Analysez d'abord les messages texte et/ou les notes vocales pour voir les résultats globaux")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 4 : CONFORMITÉ FORENSIQUE
    # ═══════════════════════════════════════════════════════════════
    
    with tab4:
        st.header("🔐 Conformité Forensique - ISO 27037")
        
        st.markdown("""
        ### ✅ Standards appliqués
        
        **ISO/IEC 27037:2012** - Lignes directrices pour l'identification, la collecte, 
        l'acquisition et la préservation de preuves numériques.
        
        #### 📋 Phases appliquées :
        1. **Identification** : Base msgstore.db + notes vocales identifiées
        2. **Collection** : Extraction forensique documentée
        3. **Acquisition** : Hash MD5/SHA-256 calculés
        4. **Préservation** : Chain of Custody maintenue
        """)
        
        db_file = st.session_state.get('db_file', None)
        audio_files = st.session_state.get('audio_files', None)
        
        if db_file or audio_files:
            st.subheader("🔐 Calcul des hash d'intégrité")
            
            if st.button("Calculer les hash MD5/SHA256"):
                with st.spinner("Calcul en cours..."):
                    afficher_hash_files(db_file, audio_files)
        
        st.subheader("📋 Chain of Custody")
        
        if st.button("Générer Chain of Custody"):
            generer_chain_of_custody()

# ═══════════════════════════════════════════════════════════════
    # TAB 5 : RAPPORT IA (AVEC BARRE DE PROGRESSION ET EXPORT PDF)
    # ═══════════════════════════════════════════════════════════════
    with tab5:
        st.header("📝 Génération du Rapport d'Investigation Mobile")

        st.info("""
        Ce module génère un rapport d'investigation **limité au périmètre Mobile / WhatsApp / NLP / Audio**.
        Le rapport est produit à partir des messages texte et des notes vocales analysés.
        """)

        text_results = st.session_state.get('text_results', [])
        audio_results = st.session_state.get('audio_results', [])
        if 'rapport_mobile_ia' not in st.session_state:
            st.session_state['rapport_mobile_ia'] = None

        if not text_results and not audio_results:
            st.warning("⚠️ Veuillez d'abord analyser les messages texte et/ou les notes vocales.")
        else:
            st.success("✅ Les données nécessaires sont disponibles pour générer le rapport.")
            api_key = _get_gemini_api_key_mobile()
            if api_key:
                st.success(
                    f"🔒 Clé API Gemini chargée depuis `.env` pour le modèle `{GEMINI_MODEL_NAME}`."
                )
            else:
                st.warning(
                    "⚠️ Clé Gemini introuvable. Ajoutez `GEMINI_API_KEY=...` dans le fichier `.env` "
                    "avant de générer le rapport."
                )

            # BOUTON DE GÉNÉRATION
            if st.button("🚀 Générer le rapport d'investigation", type="primary", key="generate_ai_report"):
                if not api_key:
                    st.error("❌ Échec : la clé `GEMINI_API_KEY` est requise dans le fichier `.env`.")
                else:
                    # Interface d'attente fluide
                    status_box = st.info("🔄 Initialisation du moteur d'analyse... Veuillez patienter.")
                    progress_bar = st.progress(0)
                    report_placeholder = st.empty()

                    try:
                        start_time = time.time()
                        st.session_state['rapport_mobile_ia'] = None

                        progress_bar.progress(20, text="Agrégation des données textuelles et vocales...")
                        time.sleep(0.3)

                        progress_bar.progress(40, text="Construction de la requête forensic...")
                        status_box.info("🧠 Préparation du contexte d'analyse mobile pour Gemini Flash...")
                        time.sleep(0.3)

                        progress_bar.progress(65, text="Connexion à l'API Gemini et rédaction en cours...")
                        status_box.info("🧠 Le modèle Gemini Flash rédige le rapport. Veuillez patienter...")

                        progression_stream = {"valeur": 65}

                        def afficher_generation_en_direct(texte_partiel):
                            nouvelle_valeur = min(88, 65 + len(texte_partiel) // 700)
                            if nouvelle_valeur > progression_stream["valeur"]:
                                progression_stream["valeur"] = nouvelle_valeur
                                progress_bar.progress(
                                    nouvelle_valeur,
                                    text="Rédaction du rapport par Gemini Flash..."
                                )
                            report_placeholder.markdown(texte_partiel + " ▌")

                        rapport = generer_rapport_mobile_ia(
                            text_results,
                            audio_results,
                            on_chunk=afficher_generation_en_direct
                        )

                        progress_bar.progress(90, text="Mise en page et validation du document final...")
                        clean_report = rapport.replace("```text", "").replace("```markdown", "").replace("```", "").strip()

                        if not clean_report:
                            raise ValueError("Gemini a retourne une reponse vide. Verifiez la cle API et le contenu fourni.")

                        report_placeholder.markdown(clean_report + "\n\n`Préparation de l'affichage final...`")
                        st.session_state['rapport_mobile_ia'] = clean_report

                        progress_bar.progress(100, text="Terminé !")
                        time.sleep(0.3)

                        status_box.empty()
                        progress_bar.empty()
                        report_placeholder.empty()

                        temps_ecoule = round(time.time() - start_time, 2)
                        st.success(f"✅ Rapport généré avec succès en {temps_ecoule} secondes.")

                    except Exception as e:
                        status_box.empty()
                        progress_bar.empty()
                        report_placeholder.empty()
                        st.error(f"❌ Erreur lors de la génération du rapport : {str(e)}")

            # AFFICHAGE DU RÉSULTAT ET BOUTON PDF (Hors de la boucle du bouton)
            if st.session_state.get('rapport_mobile_ia'):
                try:
                    pdf_bytes = generate_pdf_report(st.session_state['rapport_mobile_ia'])
                except Exception as e:
                    st.error(f"❌ Erreur lors de la preparation du PDF : {str(e)}")
                else:
                    st.download_button(
                        label="📥 Exporter le Rapport Officiel (Format PDF)",
                        data=pdf_bytes,
                        file_name="Rapport_Expertise_Mobile_2026_TC.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

                # 2. Design CSS "Format Papier"
                st.markdown("""
                <style>
                    .report-container {
                        background-color: #ffffff;
                        padding: 50px;
                        border-radius: 4px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                        margin-top: 20px;
                        margin-bottom: 20px;
                        border-top: 15px solid #1e3a8a;
                        font-family: 'Times New Roman', Times, serif;
                        color: #111827;
                        line-height: 1.6;
                    }
                    .report-container h1, .report-container h2, .report-container h3 {
                        color: #0f172a;
                        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # 3. Affichage du texte dans le cadre
                st.markdown(f'<div class="report-container">{st.session_state["rapport_mobile_ia"]}</div>', unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════
# SYSTÈME NLP - ANALYSE DE TEXTE
# ═══════════════════════════════════════════════════════════════════

def analyser_texte_nlp(texte):
    """Analyse un texte avec le système NLP de détection de patterns"""
    texte_minuscule = texte.lower()
    score = 0
    patterns_detectes = []
    
    # Chercher les patterns
    for categorie, infos in PATTERNS_SUSPECTS.items():
        mots_trouves = [mot for mot in infos['mots'] if mot in texte_minuscule]
        
        if mots_trouves:
            points_categorie = len(mots_trouves) * infos['points']
            score += points_categorie
            patterns_detectes.append({
                'categorie': categorie,
                'mots_trouves': mots_trouves,
                'points': points_categorie,
                'niveau': infos['niveau']
            })
    
    # Bonus contextuels
    nb_mots = len(texte.split())
    
    if nb_mots > 50 and patterns_detectes:
        score += 2
    
    if len(patterns_detectes) >= 2:
        score += 3
    
    # Plafonner à 20
    score = min(score, 20)
    
    # Niveau de risque
    if score >= 10:
        niveau_risque = "CRITIQUE"
        couleur = "🔴"
    elif score >= 6:
        niveau_risque = "ÉLEVÉ"
        couleur = "🟠"
    elif score >= 3:
        niveau_risque = "MOYEN"
        couleur = "🟡"
    else:
        niveau_risque = "NORMAL"
        couleur = "✅"
    
    return {
        'score': score,
        'niveau_risque': niveau_risque,
        'couleur': couleur,
        'patterns_detectes': patterns_detectes,
        'est_suspect': score >= 3
    }


# ═══════════════════════════════════════════════════════════════════
# ANALYSE MESSAGES WHATSAPP
# ═══════════════════════════════════════════════════════════════════

def analyser_messages_whatsapp(db_file):
    """Analyse les messages WhatsApp depuis msgstore.db"""
    
    # Sauvegarder temporairement le fichier
    temp_path = "temp_msgstore.db"
    with open(temp_path, "wb") as f:
        f.write(db_file.getbuffer())
    
    try:
        # Connexion SQLite
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Extraire les messages
        query = """
        SELECT 
            _id,
            key_from_me,
            key_remote_jid,
            data,
            timestamp
        FROM messages
        WHERE data IS NOT NULL
        ORDER BY timestamp
        """
        
        cursor.execute(query)
        messages = cursor.fetchall()
        conn.close()
        
        # Analyser chaque message
        resultats = []
        for msg in messages:
            msg_id, from_me, contact, texte, timestamp = msg
            
            if texte:
                analyse = analyser_texte_nlp(texte)
                
                resultats.append({
                    'id': msg_id,
                    'texte': texte,
                    'timestamp': timestamp,
                    'contact': contact,
                    'from_me': from_me,
                    **analyse
                })
        
        return resultats
    
    finally:
        # Nettoyer
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ═══════════════════════════════════════════════════════════════════
# TRANSCRIPTION WHISPER DYNAMIQUE (OPTIMISÉ CPU i9)
# ═══════════════════════════════════════════════════════════════════

def transcrire_et_analyser_whisper(audio_files):
    """
    Transcrit les fichiers audio avec Whisper et analyse avec NLP
    Optimisé pour CPU i9, sans fallback externe
    """

    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "Le package openai-whisper n'est pas installe. Installez-le avec : pip install openai-whisper"
        )

    cache_dir = _whisper_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)

    if _whisper_model_cached(WHISPER_MODEL_NAME):
        st.info(f"📥 Chargement du modèle Whisper '{WHISPER_MODEL_NAME}' depuis le cache local...")
    else:
        st.warning(
            f"⚠️ Le modèle Whisper '{WHISPER_MODEL_NAME}' n'est pas encore en cache local. "
            "Le premier lancement doit le télécharger."
        )
        st.caption(f"Cache attendu : `{cache_dir}`")

    try:
        model = whisper.load_model(
            WHISPER_MODEL_NAME,
            download_root=cache_dir
        )
    except Exception as e:
        raise RuntimeError(
            f"Impossible de charger le modèle Whisper '{WHISPER_MODEL_NAME}'. "
            f"Détail : {str(e)}. "
            f"Préchargez le modèle une fois avec : {_commande_prechargement_whisper()}"
        ) from e

    st.success(f"✅ Modèle Whisper '{WHISPER_MODEL_NAME}' chargé !")

    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)

    resultats = []
    erreurs = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        for i, audio_file in enumerate(audio_files):
            progress = (i + 1) / len(audio_files)
            progress_bar.progress(progress)
            status_text.text(
                f"Transcription {i+1}/{len(audio_files)} avec Whisper {WHISPER_MODEL_NAME} : {audio_file.name}"
            )

            start_time = time.time()
            temp_audio_path = None

            try:
                extension = os.path.splitext(audio_file.name)[1].lower() or ".ogg"
                temp_audio_path = os.path.join(temp_dir, f"audio_{i}{extension}")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                result = model.transcribe(
                    temp_audio_path,
                    language="fr",
                    fp16=False,
                    verbose=False
                )
                texte_transcrit = result["text"].strip()

                if not texte_transcrit:
                    raise ValueError("Transcription vide reçue pour ce fichier.")

                temps_transcription = time.time() - start_time

                analyse = analyser_texte_nlp(texte_transcrit)

                resultats.append({
                    'numero': i + 1,
                    'fichier': audio_file.name,
                    'texte': texte_transcrit,
                    'nb_caracteres': len(texte_transcrit),
                    'temps_transcription': temps_transcription,
                    'moteur_transcription': f"Whisper {WHISPER_MODEL_NAME}",
                    **analyse
                })

            except Exception as e:
                erreurs.append(audio_file.name)
                st.warning(f"⚠️ Erreur pour {audio_file.name} : {str(e)}")
                continue

            finally:
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

        progress_bar.empty()
        status_text.empty()

        if not resultats:
            raise RuntimeError(
                "Aucun fichier audio n'a pu être transcrit. "
                "Vérifiez le modèle Whisper local, ffmpeg et les fichiers audio fournis."
            )

        if erreurs:
            st.warning(
                f"⚠️ {len(erreurs)} fichier(s) n'ont pas pu être transcrits sur {len(audio_files)}."
            )

        return resultats

    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS D'AFFICHAGE
# ═══════════════════════════════════════════════════════════════════
def generer_rapport_mobile_ia(text_results, audio_results, on_chunk=None):
    """
    Génère un rapport d'investigation forensic mobile via Gemini Flash.
    Le rapport est limité au périmètre Mobile / WhatsApp / NLP / Audio.
    """

    # =========================
    # Préparation des statistiques
    # =========================
    total_text = len(text_results)
    total_audio = len(audio_results)
    total = total_text + total_audio

    suspects_text = len([r for r in text_results if r.get('est_suspect', False)])
    suspects_audio = len([r for r in audio_results if r.get('est_suspect', False)])
    suspects_total = suspects_text + suspects_audio

    critiques_text = len([r for r in text_results if r.get('niveau_risque') == 'CRITIQUE'])
    critiques_audio = len([r for r in audio_results if r.get('niveau_risque') == 'CRITIQUE'])
    critiques_total = critiques_text + critiques_audio

    score_moyen_text = (
        sum(r.get('score', 0) for r in text_results) / total_text
        if total_text > 0 else 0
    )
    score_moyen_audio = (
        sum(r.get('score', 0) for r in audio_results) / total_audio
        if total_audio > 0 else 0
    )
    score_moyen_global = (
        sum(r.get('score', 0) for r in (text_results + audio_results)) / total
        if total > 0 else 0
    )

    # Top éléments suspects
    top_text = sorted(text_results, key=lambda x: x.get('score', 0), reverse=True)[:5]
    top_audio = sorted(audio_results, key=lambda x: x.get('score', 0), reverse=True)[:5]

    # Patterns globaux
    patterns_count = {}
    for item in text_results + audio_results:
        for p in item.get('patterns_detectes', []):
            categorie = p.get('categorie', 'inconnu')
            patterns_count[categorie] = patterns_count.get(categorie, 0) + 1

    top_patterns = sorted(patterns_count.items(), key=lambda x: x[1], reverse=True)[:10]

    # =========================
    # Données compactes envoyées au modèle
    # =========================
    payload = {
        "scope": "Investigation Mobile uniquement",
        "source_text_total": total_text,
        "source_audio_total": total_audio,
        "total_communications": total,
        "suspects_text": suspects_text,
        "suspects_audio": suspects_audio,
        "suspects_total": suspects_total,
        "critiques_text": critiques_text,
        "critiques_audio": critiques_audio,
        "critiques_total": critiques_total,
        "score_moyen_text": round(score_moyen_text, 2),
        "score_moyen_audio": round(score_moyen_audio, 2),
        "score_moyen_global": round(score_moyen_global, 2),
        "top_patterns": top_patterns,
        "top_messages_suspects": [
            {
                "id": x.get("id"),
                "texte": x.get("texte"),
                "score": x.get("score"),
                "niveau_risque": x.get("niveau_risque"),
                "patterns_detectes": x.get("patterns_detectes", [])
            }
            for x in top_text
        ],
        "top_audios_suspects": [
            {
                "fichier": x.get("fichier"),
                "texte": x.get("texte"),
                "score": x.get("score"),
                "niveau_risque": x.get("niveau_risque"),
                "patterns_detectes": x.get("patterns_detectes", [])
            }
            for x in top_audio
        ]
    }

# =========================
    # MASTER PROMPT (CALQUÉ SUR LE MODÈLE WINDOWS)
    # =========================
    prompt_rapport = f"""Agissez en tant qu'Expert Analyste DFIR (Digital Forensics and Incident Response).
    Rédigez un rapport d'investigation formel, structuré et impartial pour le dossier #2026-TC.
    Périmètre technique : Communications mobiles, extractions WhatsApp (Texte/Audio) et analyse IA (NLP).
    Sujet audité : "M. Jean Martin".

    ÉLÉMENTS FACTUELS EXTRAITS DES SCÉLLÉS (Basez votre analyse strictement sur ces points JSON) :
    {json.dumps(payload, indent=2, ensure_ascii=False)}

    INSTRUCTIONS DE RÉDACTION :
    1. TON : Académique, objectif, factuel et procédural. Évitez le sensationnalisme. Mentionnez que l'IA est une aide à l'interprétation.
    2. EN-TÊTE OBLIGATOIRE (À placer au tout début du texte) :
    🏛️ DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES (DFIR) 🏛️
    **RAPPORT D'EXPERTISE FORENSIQUE : PÔLE MOBILE & IA (NLP)**
    **Date d'émission :** 16 mars 2026
    **Référence Dossier :** #2026-TC
    **Sujet Ciblé :** M. Jean Martin

    3. STRUCTURE EXIGÉE :
    # I. RÉSUMÉ EXÉCUTIF
    # II. MÉTHODOLOGIE D'ANALYSE (NLP & ASR)
    # III. QUALIFICATION DE LA PRÉMÉDITATION (MENS REA - LANGAGE CODÉ)
    # IV. MATÉRIALISATION DES ACTES (ACTUS REUS - CORRÉLATION TEXTE/AUDIO)
    # V. ÉVALUATION DU RISQUE ET CONCLUSION TECHNIQUE

    4. FORMATAGE : Utilisez le format Markdown standard. Ne générez aucun bloc de code (```) ni d'indentation au début des lignes. Ne générez pas de JSON dans votre réponse.
    """
    
    return _generer_contenu_gemini_mobile(prompt_rapport, on_chunk=on_chunk)

def afficher_resultats_texte(results):
    """Affiche les résultats de l'analyse des messages texte"""
    
    st.subheader("📊 Résultats de l'analyse")

    if not results:
        st.warning("Aucun message à afficher")
        return
    
    # Statistiques globales
    suspects = [r for r in results if r['est_suspect']]
    critiques = [r for r in results if r['niveau_risque'] == 'CRITIQUE']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Messages analysés", len(results))
    with col2:
        st.metric("Messages suspects", f"{len(suspects)} ({len(suspects)/len(results)*100:.0f}%)")
    with col3:
        st.metric("Messages CRITIQUES", len(critiques))
    with col4:
        score_max = max([r['score'] for r in results])
        st.metric("Score maximum", f"{score_max:.1f}/20")
    
    # Graphique
    st.subheader("📈 Répartition par niveau de risque")
    
    niveaux = {}
    for r in results:
        niveau = r['niveau_risque']
        niveaux[niveau] = niveaux.get(niveau, 0) + 1
    
    fig = px.pie(
        values=list(niveaux.values()),
        names=list(niveaux.keys()),
        title="Distribution des niveaux de risque",
        color_discrete_map={
            'CRITIQUE': '#DC2626',
            'ÉLEVÉ': '#EA580C',
            'MOYEN': '#EAB308',
            'NORMAL': '#16A34A'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 3
    st.subheader("🎯 Top 3 des messages les plus suspects")
    
    top_3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    
    for i, msg in enumerate(top_3, 1):
        with st.expander(f"#{i} - Score {msg['score']:.1f}/20 - {msg['couleur']} {msg['niveau_risque']}"):
            st.markdown(f"**Message :** {msg['texte']}")
            st.markdown(f"**Score :** {msg['score']:.1f}/20")
            
            if msg['patterns_detectes']:
                st.markdown("**Patterns détectés :**")
                for pattern in msg['patterns_detectes']:
                    st.markdown(f"- **{pattern['categorie']}** : {', '.join(pattern['mots_trouves'])}")
    
    # Téléchargement
    st.download_button(
        label="📥 Télécharger le rapport JSON",
        data=json.dumps(results, indent=2, ensure_ascii=False),
        file_name="rapport_messages.json",
        mime="application/json"
    )


def afficher_resultats_audio(results):
    """Affiche les résultats de l'analyse des notes vocales"""
    
    st.subheader("📊 Résultats de l'analyse")
    
    if not results:
        st.warning("Aucune transcription à afficher")
        return
    
    # Statistiques
    suspects = [r for r in results if r['est_suspect']]
    critiques = [r for r in results if r['niveau_risque'] == 'CRITIQUE']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Notes analysées", len(results))
    with col2:
        st.metric("Notes suspectes", f"{len(suspects)} ({len(suspects)/len(results)*100:.0f}%)")
    with col3:
        st.metric("Notes CRITIQUES", len(critiques))
    with col4:
        score_max = max([r['score'] for r in results])
        st.metric("Score maximum", f"{score_max:.1f}/20")
    
    # Info Whisper
    temps_moyen = sum([r.get('temps_transcription', 0) for r in results]) / len(results)
    st.info(f"""
    ⏱️ **Performance Whisper :**
    - Temps moyen : {temps_moyen:.1f}s/fichier
    - Temps total : {sum([r.get('temps_transcription', 0) for r in results]):.1f}s
    """)
    
    # Top 3
    st.subheader("🎯 Top 3 des notes les plus suspectes")
    
    top_3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    
    for i, note in enumerate(top_3, 1):
        with st.expander(f"#{i} - {note['fichier']} - Score {note['score']:.1f}/20"):
            st.text_area("Transcription", note['texte'], height=100, key=f"t_{i}")
            st.markdown(f"**Score :** {note['score']:.1f}/20")
            
            if note['patterns_detectes']:
                st.markdown("**Patterns :**")
                for p in note['patterns_detectes']:
                    st.markdown(f"- {p['categorie']}: {', '.join(p['mots_trouves'])}")
    
    # Téléchargement
    st.download_button(
        label="📥 Télécharger le rapport JSON",
        data=json.dumps(results, indent=2, ensure_ascii=False),
        file_name="rapport_audio.json",
        mime="application/json"
    )


def afficher_vue_globale():
    """Vue globale dynamique avec indicateurs, graphiques et interprétation forensic"""

    text_results = st.session_state.get('text_results', [])
    audio_results = st.session_state.get('audio_results', [])

    total_text = len(text_results)
    total_audio = len(audio_results)
    total = total_text + total_audio

    if total == 0:
        st.info("ℹ️ Aucune donnée analysée pour le moment")
        return

    # =========================
    # Comptage global
    # =========================
    suspects_text = len([r for r in text_results if r.get('est_suspect', False)])
    suspects_audio = len([r for r in audio_results if r.get('est_suspect', False)])
    suspects_total = suspects_text + suspects_audio

    critiques_text = len([r for r in text_results if r.get('niveau_risque') == 'CRITIQUE'])
    critiques_audio = len([r for r in audio_results if r.get('niveau_risque') == 'CRITIQUE'])
    critiques_total = critiques_text + critiques_audio

    score_moyen_text = (
        sum(r.get('score', 0) for r in text_results) / total_text
        if total_text > 0 else 0
    )
    score_moyen_audio = (
        sum(r.get('score', 0) for r in audio_results) / total_audio
        if total_audio > 0 else 0
    )
    score_moyen_global = (
        sum(r.get('score', 0) for r in (text_results + audio_results)) / total
        if total > 0 else 0
    )

    taux_text = (suspects_text / total_text * 100) if total_text > 0 else 0
    taux_audio = (suspects_audio / total_audio * 100) if total_audio > 0 else 0
    taux_total = (suspects_total / total * 100) if total > 0 else 0

    # =========================
    # Niveau global
    # =========================
    if taux_total >= 60 or critiques_total >= 3 or score_moyen_global >= 8:
        niveau_global = "CRITIQUE"
        couleur = "🔴"
        couleur_css = "#DC2626"
    elif taux_total >= 40 or score_moyen_global >= 6:
        niveau_global = "ÉLEVÉ"
        couleur = "🟠"
        couleur_css = "#EA580C"
    elif taux_total >= 20 or score_moyen_global >= 3:
        niveau_global = "MOYEN"
        couleur = "🟡"
        couleur_css = "#EAB308"
    else:
        niveau_global = "FAIBLE"
        couleur = "🟢"
        couleur_css = "#16A34A"

    # =========================
    # Patterns dominants
    # =========================
    patterns_count = {}
    all_results = text_results + audio_results

    for r in all_results:
        for p in r.get('patterns_detectes', []):
            categorie = p.get('categorie', 'inconnu')
            patterns_count[categorie] = patterns_count.get(categorie, 0) + 1

    top_patterns = sorted(patterns_count.items(), key=lambda x: x[1], reverse=True)

    # =========================
    # Niveau dominant
    # =========================
    niveaux_count = {"CRITIQUE": 0, "ÉLEVÉ": 0, "MOYEN": 0, "NORMAL": 0}
    for r in all_results:
        niveau = r.get("niveau_risque", "NORMAL")
        if niveau in niveaux_count:
            niveaux_count[niveau] += 1

    niveau_dominant = max(niveaux_count, key=niveaux_count.get)

    # =========================
    # Source la plus risquée
    # =========================
    if total_text == 0 and total_audio > 0:
        source_risque = "Notes vocales"
    elif total_audio == 0 and total_text > 0:
        source_risque = "Messages texte"
    elif taux_text > taux_audio:
        source_risque = "Messages texte"
    elif taux_audio > taux_text:
        source_risque = "Notes vocales"
    else:
        source_risque = "Équivalent entre les deux sources"

    # =========================
    # HEADER GLOBAL
    # =========================
    st.markdown("## 📊 Vue d'Ensemble de l'Analyse")
    st.markdown(
        f"""
        <div style="
            background-color: #F8FAFC;
            border-left: 6px solid {couleur_css};
            padding: 18px;
            border-radius: 10px;
            margin-bottom: 15px;">
            <h4 style="margin: 0; color: {couleur_css};">
                {couleur} Niveau Global d'Alerte : {niveau_global}
            </h4>
            <p style="margin-top: 8px; color: #334155;">
                Cette synthèse est générée automatiquement à partir des analyses
                effectuées dans les onglets <b>Messages Texte</b> et <b>Notes Vocales</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # KPIs principaux
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total communications", total)

    with col2:
        st.metric("Éléments suspects", f"{suspects_total}", f"{taux_total:.1f}%")

    with col3:
        st.metric("Éléments critiques", critiques_total)

    with col4:
        st.metric("Score moyen global", f"{score_moyen_global:.1f}/20")

    st.markdown("---")

    # =========================
    # Répartition Texte vs Audio
    # =========================
    st.subheader("📂 Répartition par Source")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📝 Messages Texte")
        st.metric("Total texte", total_text)
        st.metric("Suspects texte", f"{suspects_text}/{total_text}" if total_text > 0 else "0/0")
        st.metric("Score moyen texte", f"{score_moyen_text:.1f}/20")
        st.progress(min(int(taux_text), 100))
        st.caption(f"Taux de suspicion texte : {taux_text:.1f}%")

    with c2:
        st.markdown("### 🎙️ Notes Vocales")
        st.metric("Total audio", total_audio)
        st.metric("Suspects audio", f"{suspects_audio}/{total_audio}" if total_audio > 0 else "0/0")
        st.metric("Score moyen audio", f"{score_moyen_audio:.1f}/20")
        st.progress(min(int(taux_audio), 100))
        st.caption(f"Taux de suspicion audio : {taux_audio:.1f}%")

    st.markdown("---")

    # =========================
    # Graphique comparatif
    # =========================
    st.subheader("📈 Comparaison Texte vs Audio")

    data_compare = pd.DataFrame({
        'Source': ['Messages Texte', 'Notes Vocales'],
        'Total': [total_text, total_audio],
        'Suspects': [suspects_text, suspects_audio],
        '% Suspects': [taux_text, taux_audio],
        'Score Moyen': [score_moyen_text, score_moyen_audio]
    })

    fig_compare = px.bar(
        data_compare,
        x='Source',
        y=['Total', 'Suspects'],
        barmode='group',
        title="Comparaison du volume et des éléments suspects"
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # =========================
    # Répartition des niveaux
    # =========================
    st.subheader("🎯 Répartition des Niveaux de Risque")

    niveaux_df = pd.DataFrame({
        'Niveau': list(niveaux_count.keys()),
        'Nombre': list(niveaux_count.values())
    })

    fig_niveaux = px.pie(
        niveaux_df,
        values='Nombre',
        names='Niveau',
        title="Distribution des niveaux de risque"
    )
    st.plotly_chart(fig_niveaux, use_container_width=True)

    # =========================
    # Top patterns détectés
    # =========================
    st.subheader("🧩 Patterns Linguistiques Dominants")

    if top_patterns:
        patterns_df = pd.DataFrame(top_patterns[:5], columns=['Pattern', 'Occurrences'])
        fig_patterns = px.bar(
            patterns_df,
            x='Pattern',
            y='Occurrences',
            title="Top 5 des patterns détectés"
        )
        st.plotly_chart(fig_patterns, use_container_width=True)

        for i, (pattern, nb) in enumerate(top_patterns[:5], start=1):
            st.markdown(f"**{i}. {pattern}** — {nb} occurrence(s)")
    else:
        st.info("Aucun pattern significatif détecté dans les données analysées.")

    st.markdown("---")

    # =========================
    # Top éléments suspects
    # =========================
    st.subheader("🚨 Top 5 des Communications les Plus Suspectes")

    top_suspects = sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)[:5]

    if top_suspects:
        for i, item in enumerate(top_suspects, start=1):
            type_source = "Texte" if item in text_results else "Audio"
            titre = item.get('fichier', f"Communication #{i}")
            contenu = item.get('texte', 'Contenu non disponible')

            with st.expander(
                f"#{i} | {type_source} | Score {item.get('score', 0):.1f}/20 | {item.get('couleur', '⚪')} {item.get('niveau_risque', 'N/A')}"
            ):
                if type_source == "Audio":
                    st.markdown(f"**Fichier audio :** {titre}")

                st.markdown(f"**Contenu :** {contenu}")
                st.markdown(f"**Score :** {item.get('score', 0):.1f}/20")
                st.markdown(f"**Niveau :** {item.get('niveau_risque', 'N/A')}")

                patterns = item.get('patterns_detectes', [])
                if patterns:
                    st.markdown("**Patterns détectés :**")
                    for p in patterns:
                        st.markdown(
                            f"- **{p.get('categorie', 'inconnu')}** : {', '.join(p.get('mots_trouves', []))}"
                        )
                else:
                    st.caption("Aucun pattern détaillé disponible pour cet élément.")
    else:
        st.info("Aucune communication suspecte majeure à afficher.")

    st.markdown("---")

    # =========================
    # Interprétation forensic dynamique
    # =========================
    st.subheader("🧠 Interprétation Forensique")

    if top_patterns:
        top_patterns_str = ", ".join([f"{nom} ({nb})" for nom, nb in top_patterns[:3]])
    else:
        top_patterns_str = "aucun pattern dominant"

    st.markdown(f"""
### {couleur} Conclusion automatisée

**1. Synthèse quantitative**
- Total analysé : **{total}** communication(s)
- Communications suspectes : **{suspects_total} ({taux_total:.1f}%)**
- Communications critiques : **{critiques_total}**
- Niveau dominant observé : **{niveau_dominant}**

**2. Corrélation des sources**
L'analyse combine les résultats issus :
- des **messages texte WhatsApp**
- des **notes vocales transcrites par Whisper**

La source actuellement la plus exposée est : **{source_risque}**

**3. Lecture technique**
Le moteur d'analyse a détecté principalement les patterns suivants :
**{top_patterns_str}**.

Le score moyen global observé est de **{score_moyen_global:.1f}/20**, ce qui classe
automatiquement l'ensemble au niveau **{niveau_global}**.

**4. Interprétation forensic**
Ces résultats constituent une **aide à l'interprétation** basée sur :
- le contenu textuel analysé,
- les expressions codées ou ambiguës détectées,
- la répétition des patterns suspects,
- la convergence entre plusieurs sources numériques.

Dans une démarche forensic, cela permet de **prioriser les éléments à examiner**
et de cibler les communications nécessitant une validation humaine.

**5. Conformité méthodologique**
Cette vue d'ensemble reste cohérente avec une approche forensic :
- préservation des données sources,
- analyse traçable,
- corrélation multi-source,
- validation finale par analyste DFIR.

**6. Conclusion**
Le système estime que le dossier présente un niveau de risque global **{niveau_global}**.
Une corrélation complémentaire avec les artefacts système, réseau, temporels
et contextuels est recommandée pour confirmer l'interprétation.
""")

def afficher_hash_files(db_file, audio_files):
    """Hash des fichiers"""
    
    if db_file:
        md5 = hashlib.md5(db_file.getvalue()).hexdigest()
        st.code(f"msgstore.db - MD5: {md5}")
    
    if audio_files:
        for audio in audio_files[:3]:
            md5 = hashlib.md5(audio.getvalue()).hexdigest()
            st.code(f"{audio.name} - MD5: {md5}")


def generer_chain_of_custody():
    """Chain of Custody"""
    
    doc = f"""
CHAIN OF CUSTODY - TECHCORP-2026-001
Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}
Analyste : Ahmed Dany
Méthode ASR : Whisper 'tiny' (CPU optimisé)
Standard : ISO 27037
"""
    
    st.text_area("Chain of Custody", doc, height=200)
    st.download_button("📥 Télécharger", doc, "chain_of_custody.txt")


if __name__ == "__main__":
    run()
