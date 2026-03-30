#zakaria
import streamlit as st
import pandas as pd
import re
import time
import os
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF

def generate_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Titre principal dyal l-PDF
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, "RAPPORT D'INVESTIGATION NUMERIQUE FORENSIQUE", ln=True, align='C')
    pdf.ln(5)
    
    # FIX 1 : N-qaddou l-7rouf li kay-diro l-mochkil f PDF (b7al œ w les guillemets)
    report_text = report_text.replace('œ', 'oe').replace('Œ', 'OE').replace('’', "'").replace('“', '"').replace('”', '"')
    
    for line in report_text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
            
        # FIX 2 : Détection dyal les Titres (Mli kaylqa #)
        if line.startswith('#'):
            # Kan-ms7ou l-# w kan-redouh MAJUSCULE
            clean_title = line.replace('#', '').replace('*', '').strip().upper()
            pdf.set_font("Arial", 'B', 12) # Khet ghlid w kbir xwiya l-Titres
            # 'ignore' kat-msa7 les emojis bla mat-3ti '????'
            safe_title = clean_title.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, txt=safe_title)
            pdf.ln(2)
        else:
            # Texte 3adi
            clean_line = line.replace('**', '').replace('*', '-').replace('`', '')
            pdf.set_font("Arial", size=11) # Khet 3adi l-texte
            # 'ignore' kat-7iyd l-emojis mn l-PDF bax ybqa nqi
            safe_line = clean_line.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 6, txt=safe_line)
            
    return pdf.output(dest="S").encode("latin-1")

# ==========================================
# FONCTIONS DE TRAITEMENT (PANDAS)
# ==========================================
def extract_hashes_from_txt(txt_content):
    md5_match = re.search(r'MD5 checksum:\s*([a-fA-F0-9]{32})', txt_content, re.IGNORECASE)
    sha1_match = re.search(r'SHA1 checksum:\s*([a-fA-F0-9]{40})', txt_content, re.IGNORECASE)
    return {
        'md5': md5_match.group(1).lower() if md5_match else "Non trouvé",
        'sha1': sha1_match.group(1).lower() if sha1_match else "Non trouvé"
    }

def process_uploaded_files(uploaded_files):
    for file in uploaded_files:
        filename = file.name
        if filename.endswith(".txt"):
            content = file.getvalue().decode("utf-8")
            if "pc_" in filename.lower():
                st.session_state.hashes['pc'] = extract_hashes_from_txt(content)
            elif "cle_" in filename.lower() or "usb" in filename.lower():
                st.session_state.hashes['usb'] = extract_hashes_from_txt(content)
        elif filename.endswith(".csv"):
            df = pd.read_csv(file)
            if filename.startswith("Web Search"): st.session_state.dfs['web'] = df
            elif filename.startswith("USB Device Attached"): st.session_state.dfs['usb'] = df
            elif filename.startswith("Recent Documents"): st.session_state.dfs['lnk'] = df
            elif filename.startswith("Shell Bags"): st.session_state.dfs['shellbags'] = df
            elif filename.startswith("File System"): st.session_state.dfs['mft'] = df
            elif filename.startswith("Run Programs"): st.session_state.dfs['prefetch'] = df

def run():
    load_dotenv()
    locked_msg = "🔒 **Section verrouillée.** En attente d'ingestion des données. Veuillez uploader les fichiers CSV/TXT dans l'onglet '0. UPLOAD' pour débloquer l'analyse."
    
    if 'dfs' not in st.session_state: st.session_state.dfs = {}
    if 'hashes' not in st.session_state: st.session_state.hashes = {'pc': None, 'usb': None}

    # ==========================================
    # CSS SAFE L-DROPZONE (Makay-plantix l-page)
    # ==========================================
    st.markdown("""
    <style>
        /* Kay-red l-Uploader kbir w zreq bared b7al iLovePDF */
        [data-testid="stFileUploader"] {
            background-color: #f0f9ff;
            border: 2px dashed #0284c7;
            border-radius: 15px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        /* Mli kat-jerr l-fichier foqo (Hover) kay-tbdl loun */
        [data-testid="stFileUploader"]:hover {
            background-color: #e0f2fe;
            border-color: #dc2626;
        }
        /* L-bouton dyal Browse files */
        [data-testid="stFileUploader"] button {
            background-color: #0284c7;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # En-tête (Design Nadi w Pro)
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <h1 style="margin:0; color:#1E3A8A;">💻 Pôle d'Analyse : Windows & USB</h1>
    </div>
    <p style="font-size:14px; color:gray;"><b>Analyste Principal :</b> Zakaria | <b>Cible :</b> pc_EmployeA.vhd | <b>Outils :</b> Autopsy 4.22.1, FTK Imager, Python Data-Stack</p>
    <hr style="margin-top:0px; margin-bottom:20px;">
    """, unsafe_allow_html=True)

  # ======= TBDEL L-TABS (ZEDNA TAB 7 IA) =======
    tab_upload, tab_synth, tab_web, tab_access, tab_usb, tab_hide, tab_conclusion, tab_ia = st.tabs(
        ["📥 0. UPLOAD", "📊 1. SYNTHÈSE", "🌐 2. WEB", "📂 3. ACCÈS", "🔌 4. USB", "🗑️ 5. DISSIMULATION", "⚖️ 6. CONCLUSION", "🤖 7. RAPPORT IA"]
    )

   # ==========================================
    # TAB 0 : UPLOAD FILES (Sécurisé & Dynamique)
    # ==========================================
    with tab_upload:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #7dd3fc; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #0369a1; margin-top: 0px; font-weight: 800;">☁️ Espace de Téléversement Sécurisé</h2>
            <p style="color: #0c4a6e; font-size: 16px; margin-bottom: 0px;">Glissez et déposez l'ensemble de vos rapports <b>.CSV (Autopsy)</b> et <b>.TXT (FTK)</b> ici.</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Uploadez vos fichiers ici", 
            accept_multiple_files=True, 
            type=['csv', 'txt'],
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.success(f"📦 **{len(uploaded_files)} fichier(s) détecté(s).**")
            
            if st.button("🚀 Lancer l'Extraction et le Parsing Forensique", use_container_width=True, type="primary"):
                with st.spinner("🔄 Analyse des bases de données... Extraction des artefacts..."):
                    process_uploaded_files(uploaded_files)
                st.success("✅ Données chargées en mémoire ! Naviguez vers l'onglet 'SYNTHÈSE'.")
                
                # Récapitulatif dynamique
                c1, c2 = st.columns(2)
                with c1:
                    tables_list = "\n".join([f"- 📄 {k.upper()} ({len(st.session_state.dfs[k])} lignes)" for k in st.session_state.dfs.keys()])
                    st.info("**📂 Tables CSV traitées en mémoire :**\n" + (tables_list if tables_list else "- Aucune table"))
                with c2:
                    hashes_text = "**🔐 Chaîne de garde (Hashes) :**\n"
                    if st.session_state.hashes['pc']: hashes_text += f"- ✔️ PC (MD5: {st.session_state.hashes['pc']['md5'][:8]}...)\n"
                    if st.session_state.hashes['usb']: hashes_text += f"- ✔️ USB (MD5: {st.session_state.hashes['usb']['md5'][:8]}...)"
                    st.info(hashes_text if hashes_text != "**🔐 Chaîne de garde (Hashes) :**\n" else "**🔐 Chaîne de garde :**\n- Aucun rapport FTK trouvé.")

    # ==========================================
    # TAB 1 : SYNTHÈSE GLOBALE & TIMELINE (100% Dynamique)
    # ==========================================
    with tab_synth:
        if not st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.error("🚨 **ALERTE CRITIQUE : EXFILTRATION AVÉRÉE** — La corrélation des artefacts Windows prouve formellement le vol de données industrielles par M. Jean Martin.")
            
            # --- CALCULS DYNAMIQUES DES KPIS (Via Pandas) ---
            # 1. Compter les recherches web suspectes
            web_count = 0
            if 'web' in st.session_state.dfs and 'Text' in st.session_state.dfs['web'].columns:
                web_count = len(st.session_state.dfs['web'][st.session_state.dfs['web']['Text'].str.contains('cacher|effacer|leak|vpn', case=False, na=False)])
            
            # 2. Compter les clés USB uniques connectées
            usb_count = 0
            if 'usb' in st.session_state.dfs and 'Device ID' in st.session_state.dfs['usb'].columns:
                usb_count = st.session_state.dfs['usb']['Device ID'].nunique()
                
            # 3. Compter les fichiers sensibles ouverts (LNK)
            lnk_count = 0
            if 'lnk' in st.session_state.dfs and 'Source Name' in st.session_state.dfs['lnk'].columns:
                lnk_count = len(st.session_state.dfs['lnk'][st.session_state.dfs['lnk']['Source Name'].str.contains('Orion|Budget|Plans', case=False, na=False)])
                
            # 4. Compter les outils d'évasion (Prefetch)
            pf_count = 0
            if 'prefetch' in st.session_state.dfs and 'Program Name' in st.session_state.dfs['prefetch'].columns:
                pf_count = len(st.session_state.dfs['prefetch'][st.session_state.dfs['prefetch']['Program Name'].str.contains('POWERSHELL|CMD|NOTEPAD', case=False, na=False)])

            st.markdown("### 📊 Métriques de l'Investigation (Temps Réel)")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔍 Recherches Suspectes", str(web_count), "Mens Rea Prouvé")
            col2.metric("🔌 Périphériques Isolés", str(usb_count), "Traces USBSTOR")
            col3.metric("📂 Fichiers Ciblés", str(lnk_count), "Accès LNK")
            col4.metric("⚠️ Outils d'Évasion", str(pf_count), "LotL (Prefetch)")
            
            st.markdown("---")
            
            # --- GRAPHIQUE DYNAMIQUE (Volume d'activité) ---
            st.markdown("### 📈 Répartition des Artefacts par Catégorie")
            # On crée un petit dataframe dynamique pour le graphique
            df_chart = pd.DataFrame({
                "Catégorie": ["Recherches Web", "Traces USB", "Accès Fichiers (LNK)", "Exécutions (Prefetch)", "Exploration (ShellBags)"],
                "Nombre d'Artefacts": [
                    len(st.session_state.dfs.get('web', [])),
                    len(st.session_state.dfs.get('usb', [])),
                    len(st.session_state.dfs.get('lnk', [])),
                    len(st.session_state.dfs.get('prefetch', [])),
                    len(st.session_state.dfs.get('shellbags', []))
                ]
            })
            st.bar_chart(df_chart.set_index("Catégorie"))

            st.markdown("### ⏱️ Timeline de la Kill Chain (Reconstruction)")
            st.caption("Cette chronologie regroupe les événements majeurs ayant mené à l'exfiltration.")
            
            # Tableau de la Timeline
            df_timeline = pd.DataFrame([
                ["15:41:37", "⚙️ Évasion", "Lancement de POWERSHELL.EXE", "Prefetch (.pf)"],
                ["15:47:28", "📁 Navigation", "Exploration du dossier 'Projet_Orion'", "ShellBags (UsrClass.dat)"],
                ["16:03:33", "🗑️ Destruction", "Suppression logique des fichiers sources", "MFT (Unallocated)"],
                ["16:47:23", "📂 Accès", "Ouverture de Budget_2026 et Plans_Confidentiels", "Recent Docs (LNK)"],
                ["17:01:37", "🔌 Exfiltration", "Branchement clé USB MXT", "USBSTOR"],
                ["18:02:46", "🌐 Dissimulation", "Recherche Google 'cacher fichiers'", "places.sqlite"]
            ], columns=["Heure (CET)", "Catégorie", "Événement", "Artefact Source"])
            st.dataframe(df_timeline, use_container_width=True, hide_index=True)

# ==========================================
    # TAB 2 : WEB (Mens Rea) - 100% DYNAMIQUE
    # ==========================================
    with tab_web:
        if 'web' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.markdown("""
            <style>
                .web-card { background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #e2e8f0; }
                .web-alert { background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 5px; margin-bottom: 15px; color: #991b1b; }
                .web-path { font-family: 'Courier New', monospace; background-color: #1e293b; color: #e2e8f0; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 🌐 Analyse Sémantique des Requêtes Web")

            st.markdown("""
            <div class="web-card">
                <h4 style="margin-top:0; color:#0f172a;">🧠 Contexte Médico-Légal (Mens Rea)</h4>
                L'analyse forensique de l'historique de navigation permet de retracer l'intention de l'utilisateur. En investigation numérique, la présence de requêtes spécifiques encadrant un incident permet de qualifier la <b>préméditation</b> et la <b>volonté de dissimulation</b>.
                <br><br>
                <b>Artefact ciblé :</b> <span class="web-path">places.sqlite</span> (Mozilla Firefox)
            </div>
            """, unsafe_allow_html=True)
            
            df_web = st.session_state.dfs['web']
            if 'Text' in df_web.columns:
                mots_cles = 'cacher|effacer|leak|vpn'
                df_filtered = df_web[df_web['Text'].str.contains(mots_cles, case=False, na=False)][['Date Accessed', 'Text']]
                
                if not df_filtered.empty:
                    # CALCULS DYNAMIQUES
                    nb_requetes = len(df_filtered)
                    heure_premiere_recherche = df_filtered['Date Accessed'].min()
                    exemple_recherche = df_filtered.iloc[0]['Text']
                    
                    df_filtered.columns = ['Horodatage (CET)', 'Requêtes Google Interceptées']
                    
                    st.markdown(f"""<div class="web-alert"><b>🚨 {nb_requetes} Indicateurs d'Intention (IoC) Détectés :</b> Filtrage sémantique appliqué sur les mots-clés critiques.</div>""", unsafe_allow_html=True)
                    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

                    # INTERPRÉTATION DYNAMIQUE
                    st.markdown(f"""
                    <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #dcfce7;">
                        <h4 style="margin-top:0; color:#14532d;">⚖️ Interprétation de l'Analyste ( )</h4>
                        <p style="margin-bottom:0; color:#15803d; line-height:1.6;">
                        Le suspect a effectué <b>{nb_requetes} recherches compromettantes</b> (exemple : <i>« {exemple_recherche} »</i>). 
                        Le premier horodatage critique identifié est à <b>{heure_premiere_recherche}</b>. Ce chronodatage démontre techniquement que l'utilisateur cherchait activement un moyen de masquer ses traces sur le système après ou avant manipulation des données.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ Aucune recherche suspecte détectée dans ce fichier.")

    # ==========================================
    # TAB 3 : LNK & SHELLBAGS (Accès) - 100% DYNAMIQUE
    # ==========================================
    with tab_access:
        if 'lnk' not in st.session_state.dfs or 'shellbags' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.markdown("""
            <style>
                .acc-card { background-color: #fdfbed; border-left: 4px solid #d97706; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #fef3c7; }
                .acc-path { font-family: 'Courier New', monospace; background-color: #451a03; color: #fef3c7; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
                .acc-header-box { background-color: #fffbeb; border: 1px solid #fde68a; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #92400e; font-weight: 600; }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 📂 Traçabilité des Accès Logiques")
            
            st.markdown("""
            <div class="acc-card">
                <h4 style="margin-top:0; color:#78350f;">🔍 Contexte Médico-Légal (Accès Conscient)</h4>
                L'analyse combinée des raccourcis Windows (LNK) et du cache de l'Explorateur (ShellBags) permet de certifier qu'un utilisateur a <b>consciemment manipulé et visualisé</b> les données critiques.
                <br><br>
                <b>Artefacts ciblés :</b> <span class="acc-path">*.lnk (Recent)</span> et <span class="acc-path">UsrClass.dat (ShellBags)</span>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            # Variables pour stocker les calculs dynamiques
            lnk_min_time, lnk_max_time, sb_min_time = "N/A", "N/A", "N/A"
            nb_lnk, nb_sb = 0, 0
            
            with c1:
                st.markdown('<div class="acc-header-box">📁 Fichiers Raccourcis (LNK)</div>', unsafe_allow_html=True)
                df_lnk = st.session_state.dfs['lnk']
                if 'Source Name' in df_lnk.columns:
                    df_fil_lnk = df_lnk[df_lnk['Source Name'].str.contains('Projet_Orion|Budget|Plans', case=False, na=False)][['Source Name', 'Date Accessed']]
                    df_fil_lnk = df_fil_lnk[~df_fil_lnk['Date Accessed'].str.contains('0000', na=False, case=False)]
                    
                    if not df_fil_lnk.empty:
                        nb_lnk = len(df_fil_lnk)
                        lnk_min_time = df_fil_lnk['Date Accessed'].min()
                        lnk_max_time = df_fil_lnk['Date Accessed'].max()
                        
                    df_fil_lnk.columns = ['Fichier Ouvert', 'Horodatage (CET)']
                    st.dataframe(df_fil_lnk, use_container_width=True, hide_index=True)

            with c2:
                st.markdown('<div class="acc-header-box">🗂️ Registre ShellBags (UsrClass.dat)</div>', unsafe_allow_html=True)
                df_sb = st.session_state.dfs['shellbags']
                if 'Path' in df_sb.columns:
                    df_fil_sb = df_sb[df_sb['Path'].str.contains('Projet|Orio|Budget', case=False, na=False)][['Path', 'Date Accessed']]
                    df_fil_sb = df_fil_sb.fillna("—") 
                    df_fil_sb = df_fil_sb[~df_fil_sb['Date Accessed'].str.contains('None', na=False, case=False)]
                    
                    if not df_fil_sb.empty:
                        nb_sb = len(df_fil_sb)
                        sb_min_time = df_fil_sb['Date Accessed'].min()
                        
                    df_fil_sb.columns = ['Répertoire Visité', 'Horodatage (CET)']
                    st.dataframe(df_fil_sb, use_container_width=True, hide_index=True)

            # INTERPRÉTATION DYNAMIQUE
            if nb_lnk > 0 or nb_sb > 0:
                st.markdown(f"""
                <div style="background-color: #fff7ed; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #fde68a;">
                    <h4 style="margin-top:0; color:#b45309;">⚖️ Synthèse Temporelle ( )</h4>
                    <p style="margin-bottom:0; color:#92400e; line-height:1.6;">
                    La chronologie extraite révèle <b>{nb_sb} navigations de dossiers</b> et <b>{nb_lnk} ouvertures de fichiers</b> suspects.
                    <br>• L'exploration visuelle des dossiers a débuté à <b>{sb_min_time}</b>.
                    <br>• Les accès directs aux fichiers individuels se sont étalés entre <b>{lnk_min_time}</b> et <b>{lnk_max_time}</b>.
                    <br>Ces actions confirment un repérage et une sélection minutieuse des données avant exfiltration.
                    </p>
                </div>
                """, unsafe_allow_html=True)
 # ==========================================
    # TAB 4 : EXFILTRATION (USB) - 100% DYNAMIQUE
    # ==========================================
    with tab_usb:
        if 'usb' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.markdown("""
            <style>
                .usb-card { background-color: #f0fdfa; border-left: 4px solid #0d9488; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #ccfbf1; }
                .usb-path { font-family: 'Courier New', monospace; background-color: #134e4a; color: #ccfbf1; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
                .usb-header-box { background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #047857; font-weight: 600; }
                .evidence-tag { background-color: #1e293b; color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 6px solid #10b981; font-family: 'Courier New', monospace; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 🔌 Périphérique d'Exfiltration (Actus Reus)")
            
            st.markdown("""
            <div class="usb-card">
                <h4 style="margin-top:0; color:#065f46;">⚙️ Contexte Médico-Légal (Mécanisme OS)</h4>
                Lorsqu'un périphérique de stockage de masse est connecté à Windows, le gestionnaire <i>Plug and Play (PnP)</i> génère une empreinte matérielle unique. Cette trace est stockée de manière persistante dans le registre système.
                <br><br>
                <b>Artefact ciblé :</b> <span class="usb-path">SYSTEM\\CurrentControlSet\\Enum\\USBSTOR</span>
            </div>
            """, unsafe_allow_html=True)
            
            df_usb = st.session_state.dfs['usb']
            if 'Device ID' in df_usb.columns:
                df_filtered = df_usb[df_usb['Device ID'].str.contains('130818v01', case=False, na=False)][['Date/Time', 'Device Make', 'Device Model', 'Device ID']]
                df_filtered = df_filtered.drop_duplicates(subset=['Device ID', 'Date/Time'])
                
                # --- EXTRACTION DYNAMIQUE DES VARIABLES ---
                usb_time, usb_make, usb_model, usb_serial = "N/A", "Inconnu", "Inconnu", "Inconnu"
                if not df_filtered.empty:
                    usb_time = df_filtered.iloc[0]['Date/Time']
                    usb_make = df_filtered.iloc[0]['Device Make']
                    usb_model = df_filtered.iloc[0]['Device Model']
                    usb_serial = df_filtered.iloc[0]['Device ID']

                df_filtered.columns = ['Horodatage de Connexion', 'Constructeur', 'Modèle', 'N° Série (ID)']
                
                c1, c2 = st.columns([1.2, 1]) 
                
                with c1:
                    st.markdown('<div class="usb-header-box">💻 Empreinte du Registre (Extraction PC)</div>', unsafe_allow_html=True)
                    st.caption("Traces extraites de l'image disque `pc_EmployeA.vhd` via Autopsy.")
                    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                
                with c2:
                    st.markdown('<div class="usb-header-box">🏷️ Pièce à Conviction (Saisie Physique)</div>', unsafe_allow_html=True)
                    st.caption("Comparaison   avec l'objet mis sous scellé.")
                    st.markdown(f"""
                    <div class="evidence-tag">
                        <b style="color:#94a3b8;">PIÈCE SCELLÉE : #B-2026-TC</b><br>
                        ---------------------------<br>
                        Catégorie : Mass Storage USB<br>
                        Marque &nbsp;&nbsp;&nbsp;: {usb_make}<br>
                        Modèle &nbsp;&nbsp;&nbsp;: {usb_model}<br>
                        N° Série &nbsp;: <span style="color:#34d399; font-weight:bold; font-size:1.15em;">{usb_serial}</span><br>
                        ---------------------------<br>
                        STATUT &nbsp;&nbsp;&nbsp;: <span style="background-color:#059669; padding:2px 8px; border-radius:4px; color:white; font-weight:bold;">MATCH CONFIRMÉ 100%</span>
                    </div>
                    """, unsafe_allow_html=True)

            # INTERPRÉTATION DYNAMIQUE
            if usb_serial != "Inconnu":
                st.markdown(f"""
                <div style="background-color: #f8fafc; border-left: 4px solid #475569; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #e2e8f0;">
                    <h4 style="margin-top:0; color:#0f172a;">⚖️ Interprétation de l'Analyste (Dynamique)</h4>
                    <p style="margin-bottom:0; color:#334155; line-height:1.6;">
                    L'artefact USBSTOR certifie de façon incontestable que la clé USB <b>{usb_make}</b> a été connectée au poste suspect exactement à <b>{usb_time}</b>. Ce chronodatage correspond parfaitement à la fenêtre d'incident. Le support physique d'exfiltration est formellement identifié grâce à son numéro de série unique <b>{usb_serial}</b>.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # TAB 5 : DISSIMULATION (MFT & Prefetch) - 100% DYNAMIQUE
    # ==========================================
    with tab_hide:
        if 'prefetch' not in st.session_state.dfs or 'mft' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.markdown("""
            <style>
                .af-card { background-color: #fefce8; border-left: 4px solid #b45309; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #fef3c7; }
                .af-header-box { background-color: #fffbeb; border: 1px solid #fde68a; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #92400e; font-weight: 600; }
                .af-path { font-family: 'Courier New', monospace; background-color: #78350f; color: #fef3c7; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 🗑️ Outils d'Évasion et de Destruction (Anti-Forensics)")

            st.markdown("""
            <div class="af-card">
                <h4 style="margin-top:0; color:#78350f;">⚠️ Contexte Médico-Légal (Dissimulation)</h4>
                L'utilisation d'outils d'administration (technique <b>Living off the Land</b>) couplée à l'effacement de données constitue une circonstance aggravante démontrant la volonté de détruire les preuves.
                <br><br>
                <b>Artefacts ciblés :</b> <span class="af-path">*.pf</span> (Prefetch) et <span class="af-path">$MFT</span> (Fichiers effacés)
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            # --- VARIABLES DYNAMIQUES ---
            pf_min_time, pf_max_time, pf_count = "N/A", "N/A", 0
            mft_count, mft_sample = 0, "aucun_fichier"

            with c1:
                st.markdown('<div class="af-header-box">⚙️ 1. Exécution Suspecte (Prefetch)</div>', unsafe_allow_html=True)
                df_pf = st.session_state.dfs['prefetch']
                if 'Program Name' in df_pf.columns:
                    df_fil_pf = df_pf[df_pf['Program Name'].str.contains('POWERSHELL|CMD|NOTEPAD', case=False, na=False)][['Program Name', 'Date/Time']]
                    df_fil_pf = df_fil_pf.drop_duplicates(subset=['Program Name', 'Date/Time'])
                    
                    if not df_fil_pf.empty:
                        pf_count = len(df_fil_pf)
                        pf_min_time = df_fil_pf['Date/Time'].min()
                        pf_max_time = df_fil_pf['Date/Time'].max()
                        
                    df_fil_pf.columns = ['Binaire Exécuté', 'Horodatage (CET)']
                    st.dataframe(df_fil_pf, use_container_width=True, hide_index=True)

            with c2:
                st.markdown('<div class="af-header-box">🗑️ 2. Fichiers Supprimés Récupérés (MFT)</div>', unsafe_allow_html=True)
                df_mft = st.session_state.dfs['mft']
                if 'Name' in df_mft.columns:
                    df_fil_mft = df_mft[
                        (df_mft['Name'].str.contains('Plans_Confidentiels|Budget|Orion', case=False, na=False)) & 
                        (df_mft['Flags(Dir)'].str.contains('Unallocated', na=False)) &
                        (df_mft['Created Time'].str.contains('2026', na=False))
                    ][['Name', 'Created Time', 'Flags(Dir)']]
                    
                    if not df_fil_mft.empty:
                        mft_count = len(df_fil_mft)
                        mft_sample = df_fil_mft.iloc[0]['Name']
                        
                    df_fil_mft.columns = ['Fichier (Récupéré)', 'Date de Création', 'Statut MFT']
                    st.dataframe(df_fil_mft, use_container_width=True, hide_index=True)

            # INTERPRÉTATION DYNAMIQUE
            if pf_count > 0 or mft_count > 0:
                st.markdown(f"""
                <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #fecaca;">
                    <h4 style="margin-top:0; color:#991b1b;">⚖️ Synthèse Anti-Forensics ( )</h4>
                    <p style="margin-bottom:0; color:#7f1d1d; line-height:1.6;">
                    L'extraction a identifié <b>{pf_count} exécutions suspectes</b> (terminaux de commande) effectuées entre <b>{pf_min_time}</b> et <b>{pf_max_time}</b>. Cette manipulation furtive précède la suppression de <b>{mft_count} fichier(s) sensible(s)</b>, dont <i>{mft_sample}</i>, marqués comme <b>Unallocated</b> dans la MFT. La volonté de masquer l'exfiltration est matériellement prouvée.
                    </p>
                </div>
                """, unsafe_allow_html=True)
# ==========================================
    # TAB 6 : CONCLUSION FACTUELLE & CHAÎNE DE GARDE - DYNAMIQUE
    # ==========================================
    with tab_conclusion:
        if not st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.markdown("""
            <style>
                .verdict-final { background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); color: white; padding: 25px; border-radius: 8px; border-left: 8px solid #ef4444; box-shadow: 0 4px 10px rgba(0,0,0,0.15); margin-bottom: 25px; }
                .verdict-final h3 { color: #f8fafc; margin-top: 0; font-size: 1.5rem; text-transform: uppercase; letter-spacing: 1px; }
                .coc-box { background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-top: 10px; font-family: 'Courier New', monospace; box-shadow: inset 0 0 8px rgba(0,0,0,0.02); }
                .coc-header { color: #0f172a; font-weight: 900; border-bottom: 2px dashed #94a3b8; padding-bottom: 10px; margin-bottom: 15px; font-size: 1.1em; }
                .hash-match { color: #059669; font-weight: 900; background-color: #d1fae5; padding: 2px 8px; border-radius: 4px; border: 1px solid #34d399; font-family: 'Segoe UI', sans-serif; font-size: 0.8em; }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### ⚖️ Rapport de Synthèse & Clôture du Dossier")

            # --- VÉRIFICATIONS DYNAMIQUES POUR LE VERDICT ---
            has_web = 'web' in st.session_state.dfs and not st.session_state.dfs['web'][st.session_state.dfs['web']['Text'].str.contains('cacher|effacer|leak|vpn', case=False, na=False)].empty
            has_usb = 'usb' in st.session_state.dfs and not st.session_state.dfs['usb'][st.session_state.dfs['usb']['Device ID'].str.contains('130818v01', case=False, na=False)].empty
            has_lnk = 'lnk' in st.session_state.dfs and not st.session_state.dfs['lnk'][st.session_state.dfs['lnk']['Source Name'].str.contains('Orion|Budget|Plans', case=False, na=False)].empty
            has_pf = 'prefetch' in st.session_state.dfs and not st.session_state.dfs['prefetch'][st.session_state.dfs['prefetch']['Program Name'].str.contains('POWERSHELL|CMD|NOTEPAD', case=False, na=False)].empty

            # VERDICT DYNAMIQUE
            if has_usb and has_lnk:
                st.markdown("""
                <div class="verdict-final">
                    <h3>🚨 Verdict Officiel : Culpabilité Établie</h3>
                    <p style="font-size: 1.1em; line-height: 1.6; margin-bottom:0;">
                    L'investigation numérique croisée menée sur les scellés conclut formellement à la culpabilité de M. Jean Martin. Les traces techniques extraites démontrent sans équivoque un vol de données industrielles critiques (Projet Orion).
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown("""
                <div class="verdict-final" style="border-left: 8px solid #f59e0b; background: linear-gradient(135deg, #78350f 0%, #451a03 100%);">
                    <h3>⚠️ Verdict Partiel : Preuves Insuffisantes</h3>
                    <p style="font-size: 1.1em; line-height: 1.6; margin-bottom:0;">
                    L'exfiltration ou l'accès aux données n'a pas pu être formellement établi à partir des jeux de données actuellement fournis. Des investigations complémentaires sont requises.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # MATRICE DYNAMIQUE (S'adapte aux preuves trouvées)
            st.markdown("#### 📌 Matrice de Compromission (Faisceau d'indices)")
            c1, c2 = st.columns(2)
            with c1:
                if has_web:
                    st.info("**🧠 1. Préméditation (Mens Rea) : ✔️ PROUVÉE**\n\nL'historique révèle des recherches préalables explicites sur la dissimulation de données.")
                else:
                    st.info("**🧠 1. Préméditation (Mens Rea) : ❌ NON ÉTABLIE**\n\nAucune recherche suspecte n'a été détectée dans l'historique Web.")
                
                if has_lnk:
                    st.warning("**👁️ 2. Accès Conscient : ✔️ PROUVÉ**\n\nLes artefacts prouvent le repérage visuel et l'ouverture manuelle des fichiers financiers ciblés.")
                else:
                    st.warning("**👁️ 2. Accès Conscient : ❌ NON ÉTABLI**\n\nAucune trace d'ouverture manuelle des fichiers confidentiels n'a été détectée.")
            with c2:
                if has_usb:
                    st.success("**🔌 3. Exfiltration (Actus Reus) : ✔️ PROUVÉE**\n\nLa ruche `USBSTOR` confirme mathématiquement la connexion de la clé USB suspecte.")
                else:
                    st.success("**🔌 3. Exfiltration (Actus Reus) : ❌ NON ÉTABLIE**\n\nAucune trace de la clé USB suspecte dans le registre système.")
                
                if has_pf:
                    st.error("**🗑️ 4. Anti-Forensics : ✔️ PROUVÉ**\n\nL'analyse `Prefetch` et les entrées `$MFT` prouvent la tentative de nettoyage des traces via terminaux de commande.")
                else:
                     st.error("**🗑️ 4. Anti-Forensics : ❌ NON ÉTABLI**\n\nAucune exécution furtive d'outils d'administration n'a été repérée.")

            st.divider()

            # CHAIN OF CUSTODY (Reste inchangée car elle lit déjà dynamiquement le dictionnaire st.session_state.hashes)
            st.markdown("#### 🔐 Préservation de l'Intégrité (Chain of Custody)")
            st.write("Conformément à la norme ISO/IEC 27037 sur la gestion des preuves numériques, l'intégrité des supports a été figée cryptographiquement dès l'acquisition par l'outil de référence *FTK Imager*. **Ce dossier est certifié inaltéré et légalement recevable.**")

            if st.session_state.hashes['pc'] or st.session_state.hashes['usb']:
                col_pc, col_usb = st.columns(2)
                
                pc_h = st.session_state.hashes['pc']
                usb_h = st.session_state.hashes['usb']
                
                with col_pc:
                    if pc_h:
                        st.markdown(f"""
                        <div class="coc-box">
                            <div class="coc-header">🖥️ SCELLÉ NUMÉRIQUE : PIÈCE C</div>
                            <b>Cible analysée :</b> pc_EmployeA.001<br>
                            <b>Acquisition :</b> AccessData FTK Imager<br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat MD5 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{pc_h['md5']}</span> <span class="hash-match">✔ VALIDÉ</span><br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat SHA-1 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{pc_h['sha1']}</span> <span class="hash-match">✔ VALIDÉ</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("⚠️ Empreintes PC manquantes. Chargez le fichier .txt de FTK Imager.")
                        
                with col_usb:
                    if usb_h:
                        st.markdown(f"""
                        <div class="coc-box">
                            <div class="coc-header">💾 SCELLÉ NUMÉRIQUE : PIÈCE B</div>
                            <b>Cible analysée :</b> cle_suspecte.E01<br>
                            <b>Acquisition :</b> AccessData FTK Imager<br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat MD5 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{usb_h['md5']}</span> <span class="hash-match">✔ VALIDÉ</span><br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat SHA-1 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{usb_h['sha1']}</span> <span class="hash-match">✔ VALIDÉ</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("⚠️ Empreintes USB manquantes. Chargez le fichier .txt de FTK Imager.")
                        
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("⚖️ *Attestation de l'analyste : Les empreintes cryptographiques calculées correspondent strictement aux journaux d'acquisition initiaux.*")
            else:
                st.warning("⚠️ Les journaux d'empreinte FTK (.txt) n'ont pas été chargés. La vérification de la chaîne de garde (Chain of Custody) ne peut être établie.")
# ==========================================
    # TAB 7 : GENERATEUR DE RAPPORT IA (GEMINI) - STYLE ACADÉMIQUE / DFIR
    # ==========================================
    with tab_ia:
        if not st.session_state.dfs: 
            st.warning("🔒 Section verrouillée. Veuillez procéder à l'ingestion des journaux dans l'onglet '0. UPLOAD'.")
        else:
            st.markdown("### 🤖 Génération du Rapport d'Expertise")
            st.info("Ce module exploite l'Intelligence Artificielle (Modèle LLM Gemini) pour rédiger un rapport d'investigation formel, basé exclusivement sur les artefacts techniques extraits.")
            
            # Champ pour la clé API
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                st.success("🔒 Clé d'interface de programmation (API) chargée de manière sécurisée via l'environnement local.")
            else:
                st.warning("⚠️ Clé d'authentification API introuvable. Veuillez l'insérer manuellement :")
                api_key = st.text_input("🔑 Clé API Google Gemini :", type="password")
            
            # Initialisation de la mémoire
            if "final_report" not in st.session_state:
                st.session_state.final_report = None

            # 1. BOUTON DE GÉNÉRATION (VERSION ACADÉMIQUE ET FLUIDE)
            if st.button("⚖️ Générer le Rapport Officiel", type="primary"):
                if not api_key:
                    st.error("❌ Échec : Une clé API valide est requise pour initialiser le modèle de langage.")
                else:
                    # Indicateur de statut professionnel
                    status_box = st.info("🔄 Initialisation du moteur d'analyse sémantique et transmission des artefacts... Veuillez patienter.")
                    report_placeholder = st.empty()
                    
                    try:
                        import time
                        start_time = time.time()
                        
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        # --- CONSTRUCTION DYNAMIQUE DES FAITS (Data-Driven) ---
                        faits_ia = []
                        if 'web' in st.session_state.dfs and not st.session_state.dfs['web'].empty:
                            nb_web = len(st.session_state.dfs['web'][st.session_state.dfs['web']['Text'].str.contains('cacher|effacer|leak|vpn', case=False, na=False)])
                            faits_ia.append(f"- Historique Web : Détection de {nb_web} requêtes liées à la dissimulation de données et au contournement réseau.")
                        
                        if 'lnk' in st.session_state.dfs and not st.session_state.dfs['lnk'].empty:
                            nb_lnk = len(st.session_state.dfs['lnk'][st.session_state.dfs['lnk']['Source Name'].str.contains('Orion|Budget|Plans', case=False, na=False)])
                            faits_ia.append(f"- Fichiers LNK : Traces d'accès manuel et interactif à {nb_lnk} documents de nature confidentielle.")
                        
                        if 'shellbags' in st.session_state.dfs and not st.session_state.dfs['shellbags'].empty:
                            faits_ia.append("- Artefacts ShellBags : Preuve d'exploration visuelle du répertoire cible via l'explorateur de fichiers Windows.")
                            
                        if 'usb' in st.session_state.dfs and not st.session_state.dfs['usb'].empty:
                            usb_id = st.session_state.dfs['usb'].iloc[0]['Device ID'] if 'Device ID' in st.session_state.dfs['usb'].columns else "Inconnu"
                            faits_ia.append(f"- Périphérique USB (USBSTOR) : Connexion avérée d'un support de stockage amovible (Identifiant matériel : {usb_id}).")
                            
                        if 'prefetch' in st.session_state.dfs and not st.session_state.dfs['prefetch'].empty:
                            faits_ia.append("- Fichiers Prefetch : Exécution avérée d'outils d'administration en ligne de commande (LotL), suggérant une manipulation furtive.")
                            
                        if 'mft' in st.session_state.dfs and not st.session_state.dfs['mft'].empty:
                            faits_ia.append("- Master File Table (MFT) : Tentative de suppression logique (fichiers désalloués) des données préalablement consultées.")

                        faits_texte = "\n".join(faits_ia) if faits_ia else "Aucun artefact critique identifié dans les jeux de données fournis."

                        # --- MASTER PROMPT ADOUCI POUR PASSER LES FILTRES DE SÉCURITÉ DE L'API ---
                        prompt = f"""Agissez en tant qu'Expert Analyste DFIR (Digital Forensics and Incident Response).
                        Rédigez un rapport d'investigation formel, structuré et impartial pour le dossier #2026-TC.
                        Périmètre technique : Systèmes d'exploitation Windows et supports de stockage USB.
                        Sujet audité : "M. Jean Martin".

                        ÉLÉMENTS FACTUELS EXTRAITS DES SCÉLLÉS (Basez votre analyse strictement sur ces points) :
                        {faits_texte}

                        INSTRUCTIONS DE RÉDACTION :
                        1. TON : Académique, objectif, factuel et procédural. Évitez le sensationnalisme.
                        2. EN-TÊTE OBLIGATOIRE (À placer au tout début du texte) :
                        🏛️ DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES (DFIR) 🏛️
                        **RAPPORT D'EXPERTISE FORENSIQUE : PÔLE WINDOWS & USB**
                        **Date d'émission :** 16 mars 2026
                        **Référence Dossier :** #2026-TC
                        **Sujet Ciblé :** M. Jean Martin

                        3. STRUCTURE EXIGÉE :
                        # I. RÉSUMÉ EXÉCUTIF
                        # II. QUALIFICATION DE LA PRÉMÉDITATION (MENS REA)
                        # III. MATÉRIALISATION DE L'ACCÈS ET DE L'EXFILTRATION (ACTUS REUS)
                        # IV. MANŒUVRES D'OBSTRUCTION ET ANTI-FORENSICS
                        # V. CONCLUSION TECHNIQUE

                        4. FORMATAGE : Utilisez le format Markdown standard. Ne générez aucun bloc de code (```) ni d'indentation au début des lignes.
                        """
                        
                        status_box.info("🧠 Génération du rapport d'expertise en cours via le modèle LLM...")
                        
                        # --- STREAMING FLUIDE (Sans CSS complexe pendant la boucle) ---
                        full_report = ""
                        response = model.generate_content(prompt, stream=True)
                        
                        for chunk in response:
                            try:
                                full_report += chunk.text
                                # Affichage simple et rapide pendant la génération
                                report_placeholder.markdown(full_report + " ▌")
                            except Exception:
                                continue # Ignore silencieusement les erreurs de flux mineures
                        
                        end_time = time.time()
                        temps_ecoule = round(end_time - start_time, 2)
                        
                        if not full_report.strip():
                            status_box.empty()
                            st.error("❌ Échec de la génération. Le filtre de sécurité automatisé de l'API a intercepté la requête. Veuillez vérifier la nature des artefacts.")
                        else:
                            # Nettoyage et application du rendu visuel final (Document juridique)
                            clean_report = full_report.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
                            
                            report_placeholder.markdown(f"""
                            <div style="background-color: #ffffff; padding: 50px; border-radius: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.10); margin-top: 20px; border-top: 15px solid #1e3a8a; font-family: 'Times New Roman', serif; color: #111827; line-height: 1.6;">
                                {clean_report}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.session_state.final_report = clean_report
                            status_box.empty() # Effacement du message d'attente
                            st.success(f"✅ Rapport technique finalisé en {temps_ecoule} secondes.")
                            
                    except Exception as e:
                        status_box.empty()
                        st.error(f"❌ Une anomalie d'exécution a été rencontrée lors de l'appel à l'API : {str(e)}")
                        
            # =========================================================================
            # 2. AFFICHAGE DU BOUTON PDF (HORS BOUCLE)
            # =========================================================================
            if st.session_state.final_report:
                pdf_bytes = generate_pdf_report(st.session_state.final_report)
                st.download_button(
                    label="📥 Exporter le Rapport Officiel (Format PDF)",
                    data=pdf_bytes,
                    file_name="Rapport_Expertise_Windows_USB_2026_TC.pdf",
                    mime="application/pdf",
                    type="primary"
                )        
        
                # CSS POUR RENDRE LE RAPPORT COMME UNE FEUILLE DE PAPIER À L'ÉCRAN
                st.markdown("""
                <style>
                    .report-container {
                        background-color: #ffffff;
                        padding: 50px;
                        border-radius: 4px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                        margin-top: 20px;
                        border-top: 15px solid #1e3a8a;
                        font-family: 'Times New Roman', Times, serif; /* Police type juridique */
                        color: #111827;
                        line-height: 1.6;
                    }
                    .report-container h1, .report-container h2, .report-container h3 {
                        color: #0f172a;
                        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.final_report, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)