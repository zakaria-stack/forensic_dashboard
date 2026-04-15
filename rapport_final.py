import streamlit as st
import os
import time
import google.generativeai as genai

# ==========================================
# FONCTION DE GÉNÉRATION PDF
# ==========================================
def generate_pdf_report(texte_md):
    """Génère un fichier PDF propre à partir du texte Markdown"""
    try:
        from fpdf import FPDF
    except ImportError:
        return b"Erreur: La bibliotheque fpdf n'est pas installee. (pip install fpdf)"
        
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, "RAPPORT D'EXPERTISE FORENSIQUE GLOBAL - C.I.A.F.", 0, 1, 'C')
            self.ln(5)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Nettoyage du Markdown et des Emojis
    texte_clean = texte_md.replace('**', '').replace('##', '').replace('#', '').replace('🏛️', '')
    texte_clean = texte_clean.replace('🔴', '[Critique]').replace('🟠', '[Eleve]').replace('🟡', '[Moyen]').replace('🟢', '[Faible]')
    texte_clean = texte_clean.replace('→', '->').replace('•', '-')
    
    for line in texte_clean.split('\n'):
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=safe_line)
        
    return pdf.output(dest='S').encode('latin-1')


# ==========================================
# FONCTION PRINCIPALE DE L'ONGLET
# ==========================================
def run():
    st.markdown("## 📜 Générateur du Rapport Final (Global)")
    st.info("💡 Cette section consolidera automatiquement les analyses de tous les pôles (Windows, Linux, Réseau, Mobile) pour générer le rapport juridique final.")
    
    # 1. ZONE DE TÉLÉVERSEMENT GLOBAL (UPLOAD ALL)
    st.markdown("### 1. Ingestion Globale des Scellés")
    uploaded_files = st.file_uploader(
        "📂 Glissez et déposez l'ensemble des fichiers de l'enquête (CSV, TXT, DB, OGG, PCAP...)", 
        accept_multiple_files=True
    )
    
    # Variables pour compter les preuves de chaque membre
    preuves_zakaria = 0
    preuves_ismail = 0
    preuves_ahmed = 0
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) détecté(s) dans le sas d'ingestion.")
        
        # Classification automatique basée sur les noms de fichiers
        for file in uploaded_files:
            nom = file.name.lower()
            if nom.endswith('.csv') or nom.endswith('.txt') or nom.endswith('.e01') or nom.endswith('.vhd') or '001' in nom:
                preuves_zakaria += 1
            elif nom.endswith('.pcap') or 'bash_history' in nom:
                preuves_ismail += 1
            elif nom.endswith('.db') or nom.endswith('.ogg') or 'msgstore' in nom:
                preuves_ahmed += 1
                
        # Affichage du tableau de bord de l'équipe
        st.markdown("#### 🛡️ Validation des Pôles d'Investigation")
        c1, c2, c3 = st.columns(3)
        with c1:
            if preuves_zakaria > 0:
                st.success(f"💻 **Pôle Windows/USB (Zakaria)**\n\n{preuves_zakaria} artefacts chargés.")
            else:
                st.warning("💻 **Pôle Windows/USB (Zakaria)**\n\nEn attente...")
        with c2:
            if preuves_ismail > 0:
                st.success(f"🐧 **Pôle Linux/Réseau (Ismail)**\n\n{preuves_ismail} artefacts chargés.")
            else:
                st.warning("🐧 **Pôle Linux/Réseau (Ismail)**\n\nEn attente...")
        with c3:
            if preuves_ahmed > 0:
                st.success(f"📱 **Pôle Mobile/IA (Ahmed)**\n\n{preuves_ahmed} artefacts chargés.")
            else:
                st.warning("📱 **Pôle Mobile/IA (Ahmed)**\n\nEn attente...")

    st.divider()

    # 2. GÉNÉRATION DU RAPPORT GLOBAL
    st.markdown("### 2. Synthèse Assistée par Intelligence Artificielle")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("🔑 Clé API Google Gemini requise :", type="password")

    if st.button("⚖️ Générer le Rapport Global", type="primary"):
        if not uploaded_files:
            st.error("❌ Veuillez d'abord uploader les fichiers de l'enquête.")
        elif not api_key:
            st.error("❌ Une clé API valide est requise.")
        else:
            status_box = st.info("🔄 Initialisation du Commandant DFIR (IA)... Veuillez patienter.")
            progress_bar = st.progress(0)
            report_placeholder = st.empty()
            
            try:
                start_time = time.time()
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                progress_bar.progress(30, text="Croisement des preuves Windows, Réseau et Mobiles...")
                
                # --- CONSTRUCTION DYNAMIQUE DES FAITS GLOBAUX ---
                faits_globaux = f"""
                1. PÔLE WINDOWS & USB (Analyste: Zakaria) - {preuves_zakaria} preuves trouvées:
                - Préméditation : Recherches Web suspectes ("comment cacher des fichiers copiés", "techcorp data leak").
                - Actus Reus : Ouverture manuelle des fichiers LNK (Projet_Orion) et connexion d'une clé USB MXT (ID: 130818v01).
                - Anti-Forensics : Exécution de PowerShell (Prefetch) et suppression de fichiers sensibles dans la MFT.
                
                2. PÔLE SERVEUR LINUX & RÉSEAU (Analyste: Ismail) - {preuves_ismail} preuves trouvées:
                - Historique Bash : Commandes d'élévation de privilèges et de compression de données détectées sur le serveur pivot (srv-intern01).
                - Analyse PCAP : Transferts FTP non sécurisés contenant des archives volumineuses vers une IP externe.
                
                3. PÔLE MOBILE & NLP (Analyste: Ahmed) - {preuves_ahmed} preuves trouvées:
                - L'analyse IA (NLP) de la base WhatsApp a révélé l'utilisation d'un langage codé (ex: "gâteau", "recette") pour désigner les fichiers volés.
                - Les transcriptions audio (Whisper) confirment l'intention d'exfiltrer les données et la coordination avec un complice externe.
                """

                progress_bar.progress(60, text="Génération de la Super-Timeline et rédaction en cours...")
                
                # --- MASTER PROMPT GLOBAL ---
                prompt = f"""Agissez en tant que Directeur des Investigations Numériques (DFIR Commander).
                Rédigez le rapport d'expertise forensique GLOBAL et DÉFINITIF pour l'Affaire #2026-TC.
                Sujet audité : "M. Jean Martin".
                Équipe d'investigation : Zakaria (Pôle Windows/USB), Ismail (Pôle Serveur Linux & Réseau PCAP), Ahmed (Pôle Mobile & IA NLP).

                SYNTHÈSE DES PREUVES FOURNIES PAR LES PÔLES (Basez-vous strictement là-dessus) :
                {faits_globaux}

                INSTRUCTIONS DE RÉDACTION :
                1. TON : Solennel, académique, implacable et digne d'une cour de justice.
                2. EN-TÊTE OBLIGATOIRE (À placer au tout début) :
                🏛️ DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES (DFIR) 🏛️
                **RAPPORT D'EXPERTISE FORENSIQUE GLOBAL ET DÉFINITIF**
                **Date d'émission :** 15 mai 2026
                **Référence Dossier :** #2026-TC
                **Sujet Ciblé :** M. Jean Martin
                **Équipe d'Investigation :** Zakaria, Ismail, Ahmed

                3. STRUCTURE EXIGÉE :
                # I. RÉSUMÉ EXÉCUTIF GLOBAL (Synthèse de l'affaire)
                # II. RECONSTRUCTION DE L'ATTAQUE (SUPER-TIMELINE CROISÉE)
                # III. CONSOLIDATION DES PREUVES PAR PÔLE (Détaillez brièvement les trouvailles de Windows, Réseau et Mobile)
                # IV. QUALIFICATION JURIDIQUE ET INTENTION (Mens Rea, Actus Reus, Anti-Forensics)
                # V. CONCLUSION DÉFINITIVE DU DÉPARTEMENT DFIR

                4. FORMATAGE : Markdown standard. Aucun bloc de code (```). Pas d'indentation en début de ligne.
                """
                
                # --- STREAMING FLUIDE ---
                full_report = ""
                response = model.generate_content(prompt, stream=True)
                
                for chunk in response:
                    try:
                        full_report += chunk.text
                        report_placeholder.markdown(full_report + " ▌")
                    except Exception:
                        continue
                
                progress_bar.progress(100, text="Mise en page du document officiel...")
                time.sleep(0.5)
                
                clean_report = full_report.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
                st.session_state.global_report = clean_report
                
                status_box.empty()
                progress_bar.empty()
                report_placeholder.empty() 
                
                st.success(f"✅ Super-Rapport généré avec succès en {round(time.time() - start_time, 2)} secondes.")
                
            except Exception as e:
                status_box.empty()
                if 'progress_bar' in locals(): progress_bar.empty()
                st.error(f"❌ Erreur lors de l'appel à l'API : {str(e)}")

    # ==========================================
    # AFFICHAGE DU RAPPORT ET BOUTON PDF
    # ==========================================
    if "global_report" in st.session_state:
        pdf_bytes = generate_pdf_report(st.session_state.global_report)
        st.download_button(
            label="📥 Exporter le Super-Rapport Officiel (Format PDF)",
            data=pdf_bytes,
            file_name="Rapport_Global_Definitif_2026_TC.pdf",
            mime="application/pdf",
            type="primary"
        )        

        st.markdown("""
        <style>
            .global-report-container {
                background-color: #ffffff;
                padding: 50px;
                border-radius: 4px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.20);
                margin-top: 20px;
                margin-bottom: 20px;
                border-top: 15px solid #0f172a; /* Bleu très foncé pour le rapport final */
                border-left: 2px solid #e2e8f0;
                border-right: 2px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                font-family: 'Times New Roman', Times, serif;
                color: #111827;
                line-height: 1.6;
            }
            .global-report-container h1, .global-report-container h2, .global-report-container h3 {
                color: #000000;
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 5px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="global-report-container">{st.session_state.global_report}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()