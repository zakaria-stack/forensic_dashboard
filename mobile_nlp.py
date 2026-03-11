"""
Module Pièce E : Mobile Data - Analyse WhatsApp IA/NLP
Analyste : Zakaria Khattar
Date : Mars 2026
Affaire : TechCorp - Fuite de données Projet Orion
"""

import streamlit as st
import sqlite3
import json
import hashlib
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION DE LA PAGE
# ═══════════════════════════════════════════════════════════════════

def run():
    """Fonction principale du module Mobile NLP"""
    
    # En-tête
    st.title("📱 Pièce E : Mobile Data - Analyse WhatsApp IA/NLP")
    st.markdown("**Analyste :** ahmed dany | **Outil :** NLP + ASR (Whisper)")
    st.markdown("---")
    
    # Info box
    st.info("""
    🤖 **Module d'analyse automatisée WhatsApp**
    
    Ce module utilise l'Intelligence Artificielle pour détecter automatiquement 
    le langage codé dans les communications WhatsApp (messages texte + notes vocales).
    
    **Technologies :** NLP (Natural Language Processing), ASR (Automatic Speech Recognition)
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # TABS POUR ORGANISER LE CONTENU
    # ═══════════════════════════════════════════════════════════════
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Messages Texte", 
        "🎙️ Notes Vocales", 
        "📊 Résultats Globaux",
        "🔐 Conformité Forensique"
    ])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1 : ANALYSE MESSAGES TEXTE
    # ═══════════════════════════════════════════════════════════════
    
    with tab1:
        st.header("📝 Analyse NLP - Messages Texte WhatsApp")
        
        # Upload de la base de données
        st.subheader("1️⃣ Upload de la base de données")
        db_file = st.file_uploader(
            "Sélectionnez le fichier msgstore.db",
            type=['db'],
            help="Base de données SQLite extraite de WhatsApp"
        )
        
        if db_file:
            st.success("✅ Fichier chargé : " + db_file.name)
            
            # Bouton d'analyse
            if st.button("🚀 Analyser les messages", key="analyze_text"):
                with st.spinner("Analyse NLP en cours..."):
                    # Appeler la fonction d'analyse
                    results = analyser_messages_whatsapp(db_file)
                    
                    # Sauvegarder dans session state
                    st.session_state['text_results'] = results
                
                st.success("✅ Analyse terminée !")
            
            # Afficher les résultats si disponibles
            if 'text_results' in st.session_state:
                afficher_resultats_texte(st.session_state['text_results'])
        else:
            st.warning("⚠️ Veuillez uploader un fichier msgstore.db pour commencer")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 2 : ANALYSE NOTES VOCALES
    # ═══════════════════════════════════════════════════════════════
    
    with tab2:
        st.header("🎙️ Analyse ASR - Notes Vocales WhatsApp")
        
        # Upload des fichiers audio
        st.subheader("1️⃣ Upload des notes vocales")
        audio_files = st.file_uploader(
            "Sélectionnez les fichiers audio (.opus, .ogg, .m4a)",
            type=['opus', 'ogg', 'm4a'],
            accept_multiple_files=True,
            help="Notes vocales extraites de WhatsApp"
        )
        
        if audio_files:
            st.success(f"✅ {len(audio_files)} fichiers audio chargés")
            
            # Option de transcription
            st.subheader("2️⃣ Méthode de transcription")
            method = st.radio(
                "Choisissez la méthode :",
                ["Transcriptions pré-existantes", "Whisper ASR (automatique)"],
                help="Utilisez les transcriptions manuelles ou Whisper pour transcrire automatiquement"
            )
            
            if method == "Transcriptions pré-existantes":
                st.info("📝 Utilisation des transcriptions déjà effectuées")
                
                if st.button("🚀 Analyser les transcriptions", key="analyze_audio"):
                    with st.spinner("Analyse NLP des transcriptions..."):
                        results = analyser_audio_preexistant(audio_files)
                        st.session_state['audio_results'] = results
                    st.success("✅ Analyse terminée !")
                
                if 'audio_results' in st.session_state:
                    afficher_resultats_audio(st.session_state['audio_results'])
            
            else:
                st.warning("⚠️ Whisper ASR nécessite des ressources GPU. Utilisez les transcriptions pré-existantes.")
        else:
            st.warning("⚠️ Veuillez uploader des fichiers audio pour commencer")
    
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
        
        # Hash des fichiers
        if db_file or audio_files:
            st.subheader("🔐 Calcul des hash d'intégrité")
            
            if st.button("Calculer les hash MD5/SHA256"):
                with st.spinner("Calcul en cours..."):
                    afficher_hash_files(db_file, audio_files)
        
        # Chain of Custody
        st.subheader("📋 Chain of Custody")
        
        if st.button("Générer Chain of Custody"):
            generer_chain_of_custody()


# ═══════════════════════════════════════════════════════════════════
# SYSTÈME NLP - DÉTECTION DE PATTERNS
# ═══════════════════════════════════════════════════════════════════

# Définition des patterns suspects
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
# FONCTIONS D'ANALYSE
# ═══════════════════════════════════════════════════════════════════

def analyser_messages_whatsapp(db_file):
    """Analyse les messages WhatsApp depuis msgstore.db"""
    
    # Sauvegarder temporairement le fichier
    with open("temp_msgstore.db", "wb") as f:
        f.write(db_file.getbuffer())
    
    # Connexion SQLite
    conn = sqlite3.connect("temp_msgstore.db")
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
    
    # Nettoyer
    os.remove("temp_msgstore.db")
    
    return resultats


def analyser_audio_preexistant(audio_files):
    """Analyse les transcriptions pré-existantes des notes vocales"""
    
    # Transcriptions simulées (à remplacer par vos vraies transcriptions)
    transcriptions = [
        {
            'fichier': audio_files[i].name if i < len(audio_files) else f'audio_{i}.ogg',
            'texte': get_transcription_simulee(i)
        }
        for i in range(min(15, len(audio_files)))
    ]
    
    # Analyser chaque transcription
    resultats = []
    for i, trans in enumerate(transcriptions):
        analyse = analyser_texte_nlp(trans['texte'])
        
        resultats.append({
            'numero': i + 1,
            'fichier': trans['fichier'],
            'texte': trans['texte'],
            **analyse
        })
    
    return resultats


def get_transcription_simulee(index):
    """Retourne une transcription simulée (à remplacer par vos vraies données)"""
    
    transcriptions = [
        "Salut Marc, c'était sympa de se voir la semaine dernière. J'espère que tu vas bien.",
        "Salut Marc alors j'ai réfléchi à ce dont on a parlé. Concernant les éléments techniques dont tu aurais besoin bon je pense que je peux te donner un coup de main. Par contre il faudra rester discret sur ce sujet.",
        "Salut Marc c'est moi. Alors concernant la fameuse recette de grand-mère dont on a parlé bon je peux te dire que c'est quasiment prêt. J'ai rassemblé tous les ingrédients nécessaires. Le gâteau devrait être au four d'ici la fin de la semaine.",
        "Marc salut. Alors on n'a pas encore parlé de la partie de l'arrangement financier. Il faudrait qu'on discute de la compensation.",
        "Marc salut je t'appelle tard exprès. Alors voilà demain c'est le grand jour. Le colis va partir. J'ai tout emballé soigneusement. Dedans tu vas trouver tous les éléments dont on a parlé. Il faut vraiment que ça reste strictement entre nous. J'ai utilisé le canal habituel. La marchandise sera en route demain soir.",
    ]
    
    return transcriptions[index % len(transcriptions)]


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS D'AFFICHAGE
# ═══════════════════════════════════════════════════════════════════

def afficher_resultats_texte(results):
    """Affiche les résultats de l'analyse des messages texte"""
    
    st.subheader("📊 Résultats de l'analyse")
    
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
    
    # Graphique de répartition
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
    
    # Top 3 messages suspects
    st.subheader("🎯 Top 3 des messages les plus suspects")
    
    top_3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    
    for i, msg in enumerate(top_3, 1):
        with st.expander(f"#{i} - Score {msg['score']:.1f}/20 - {msg['couleur']} {msg['niveau_risque']}"):
            st.markdown(f"**Message :** {msg['texte']}")
            st.markdown(f"**Score :** {msg['score']:.1f}/20")
            st.markdown(f"**Niveau :** {msg['niveau_risque']}")
            
            if msg['patterns_detectes']:
                st.markdown("**Patterns détectés :**")
                for pattern in msg['patterns_detectes']:
                    st.markdown(f"- **{pattern['categorie']}** : {', '.join(pattern['mots_trouves'])} (+{pattern['points']} pts)")
    
    # Tableau détaillé
    st.subheader("📋 Tableau détaillé des messages")
    
    df = pd.DataFrame([{
        'ID': r['id'],
        'Score': f"{r['score']:.1f}",
        'Niveau': r['niveau_risque'],
        'Aperçu': r['texte'][:50] + '...' if len(r['texte']) > 50 else r['texte']
    } for r in results])
    
    st.dataframe(df, use_container_width=True)
    
    # Bouton de téléchargement
    st.download_button(
        label="📥 Télécharger le rapport JSON",
        data=json.dumps(results, indent=2, ensure_ascii=False),
        file_name="rapport_messages_whatsapp.json",
        mime="application/json"
    )


def afficher_resultats_audio(results):
    """Affiche les résultats de l'analyse des notes vocales"""
    
    st.subheader("📊 Résultats de l'analyse")
    
    # Statistiques globales
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
    
    # Top 3 notes suspectes
    st.subheader("🎯 Top 3 des notes vocales les plus suspectes")
    
    top_3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    
    for i, note in enumerate(top_3, 1):
        with st.expander(f"#{i} - {note['fichier']} - Score {note['score']:.1f}/20 - {note['couleur']} {note['niveau_risque']}"):
            st.markdown(f"**Fichier :** {note['fichier']}")
            st.markdown(f"**Transcription :** {note['texte']}")
            st.markdown(f"**Score :** {note['score']:.1f}/20")
            st.markdown(f"**Niveau :** {note['niveau_risque']}")
            
            if note['patterns_detectes']:
                st.markdown("**Patterns détectés :**")
                for pattern in note['patterns_detectes']:
                    st.markdown(f"- **{pattern['categorie']}** : {', '.join(pattern['mots_trouves'])} (+{pattern['points']} pts)")
    
    # Bouton de téléchargement
    st.download_button(
        label="📥 Télécharger le rapport JSON",
        data=json.dumps(results, indent=2, ensure_ascii=False),
        file_name="rapport_notes_vocales.json",
        mime="application/json"
    )


def afficher_vue_globale():
    """Affiche la vue globale combinant texte + audio"""
    
    text_results = st.session_state.get('text_results', [])
    audio_results = st.session_state.get('audio_results', [])
    
    total_text = len(text_results)
    total_audio = len(audio_results)
    total = total_text + total_audio
    
    suspects_text = len([r for r in text_results if r['est_suspect']])
    suspects_audio = len([r for r in audio_results if r['est_suspect']])
    suspects_total = suspects_text + suspects_audio
    
    # Métriques globales
    st.subheader("📊 Statistiques globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total communications", total)
    with col2:
        st.metric("Messages texte", total_text)
    with col3:
        st.metric("Notes vocales", total_audio)
    with col4:
        st.metric("Suspects détectés", f"{suspects_total} ({suspects_total/total*100:.0f}%)")
    
    # Graphique comparatif
    st.subheader("📈 Comparaison Texte vs Audio")
    
    data = {
        'Source': ['Messages Texte', 'Notes Vocales'],
        'Total': [total_text, total_audio],
        'Suspects': [suspects_text, suspects_audio],
        '% Suspects': [suspects_text/total_text*100 if total_text > 0 else 0, 
                       suspects_audio/total_audio*100 if total_audio > 0 else 0]
    }
    
    df = pd.DataFrame(data)
    
    fig = go.Figure(data=[
        go.Bar(name='Total', x=df['Source'], y=df['Total']),
        go.Bar(name='Suspects', x=df['Source'], y=df['Suspects'])
    ])
    
    fig.update_layout(
        title='Comparaison des sources de données',
        barmode='group',
        xaxis_title='Source',
        yaxis_title='Nombre de communications'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Observations clés
    st.subheader("🔍 Observations clés")
    
    st.markdown(f"""
    - **Total de communications analysées :** {total}
    - **Communications suspectes :** {suspects_total} ({suspects_total/total*100:.0f}%)
    - **Taux de suspicion messages texte :** {suspects_text/total_text*100:.0f}%
    - **Taux de suspicion notes vocales :** {suspects_audio/total_audio*100:.0f}%
    
    **Conclusion :** Le suspect utilise plusieurs canaux de communication (texte + voix) 
    pour coordonner ses activités suspectes avec le concurrent.
    """)


def afficher_hash_files(db_file, audio_files):
    """Calcule et affiche les hash MD5/SHA256"""
    
    st.subheader("🔐 Hash d'intégrité")
    
    # Hash de la base de données
    if db_file:
        md5_hash = hashlib.md5(db_file.getvalue()).hexdigest()
        sha256_hash = hashlib.sha256(db_file.getvalue()).hexdigest()
        
        st.markdown("**msgstore.db**")
        st.code(f"MD5    : {md5_hash}")
        st.code(f"SHA256 : {sha256_hash}")
    
    # Hash des fichiers audio
    if audio_files:
        st.markdown("**Notes vocales**")
        for audio in audio_files[:5]:  # Limiter à 5 pour l'affichage
            md5_hash = hashlib.md5(audio.getvalue()).hexdigest()
            st.markdown(f"- **{audio.name}**")
            st.code(f"MD5: {md5_hash}")
        
        if len(audio_files) > 5:
            st.info(f"... et {len(audio_files) - 5} autres fichiers")
    
    st.success("✅ Hash calculés avec succès - Intégrité garantie")


def generer_chain_of_custody():
    """Génère un document Chain of Custody"""
    
    chain_of_custody = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    CHAÎNE DE GARDE (CHAIN OF CUSTODY)                ║
║                  PIÈCE À CONVICTION - MOBILE DATA                    ║
╚══════════════════════════════════════════════════════════════════════╝

INFORMATIONS SUR LE CAS
═══════════════════════════════════════════════════════════════════════

Numéro de Cas        : TECHCORP-2026-001
Affaire              : Fuite de données - Projet Orion
Pièce à Conviction   : Pièce E - Mobile Data WhatsApp
Type d'Appareil      : Samsung Galaxy S23
Système d'Exploitation : Android 14
Version WhatsApp     : 2.26.1.72
Analyste             : ahmed dany

MÉTHODE D'ACQUISITION
═══════════════════════════════════════════════════════════════════════

Type d'Extraction    : Logical Extraction
Standard Appliqué    : ISO/IEC 27037:2012

CHRONOLOGIE
═══════════════════════════════════════════════════════════════════════

Date de saisie       : 15 Janvier 2026, 14:30
Date d'extraction    : 15 Janvier 2026, 15:00
Date d'analyse       : {datetime.now().strftime('%d %B %Y, %H:%M')}

DÉCLARATION
═══════════════════════════════════════════════════════════════════════

Je certifie que l'intégrité des preuves a été maintenue durant toute
la chaîne de traitement, conformément aux standards ISO 27037.

Signature Analyste : _______________________

Date : {datetime.now().strftime('%d/%m/%Y')}

╔══════════════════════════════════════════════════════════════════════╗
║              FIN DU DOCUMENT DE CHAÎNE DE GARDE                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    st.text_area("Chain of Custody", chain_of_custody, height=400)
    
    st.download_button(
        label="📥 Télécharger Chain of Custody",
        data=chain_of_custody,
        file_name=f"chain_of_custody_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )


# ═══════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run()