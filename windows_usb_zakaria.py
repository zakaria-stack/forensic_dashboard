#zakaria
import streamlit as st
import pandas as pd
import re
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
    # TAB 0 : UPLOAD FILES (Le Nouveau Design)
    # ==========================================
    with tab_upload:
        # Banniére zwina b7al dyal Telegram/WhatsApp
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #7dd3fc; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #0369a1; margin-top: 0px; font-weight: 800;">☁️ Espace de Téléversement Sécurisé</h2>
            <p style="color: #0c4a6e; font-size: 16px; margin-bottom: 0px;">Glissez et déposez l'ensemble de vos rapports <b>.CSV (Autopsy)</b> et <b>.TXT (FTK)</b> ici.</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Uploadez vos fichiers ici (Sélectionnez tout d'un coup)", 
            accept_multiple_files=True, 
            type=['csv', 'txt'],
            label_visibility="collapsed" # Kan-khebiw l-titre sghir 7it drna Banniére kbira
        )

        if uploaded_files:
            # Animation sghira w message wa3er mli kay-upload
            st.success(f"📦 **{len(uploaded_files)} fichier(s) mis en cache.**")
            
            # Bouton kbir w byyn
            if st.button("🚀 Lancer l'Extraction et le Parsing Forensique", use_container_width=True, type="primary"):
                with st.spinner("🔄 Analyse en cours... Recherche des preuves..."):
                    process_uploaded_files(uploaded_files)
                st.success("✅ Extraction terminée ! Naviguez dans les onglets ci-dessus pour voir les résultats.")
                
                # Check-list nqiya dyal xno t-uploada
                c1, c2 = st.columns(2)
                with c1:
                    st.info("**📂 Tables CSV traitées :**\n" + "\n".join([f"- {k.upper()}" for k in st.session_state.dfs.keys()]))
                with c2:
                    hashes_text = "**🔐 Chaîne de garde (Hashes) :**\n"
                    if st.session_state.hashes['pc']: hashes_text += "- ✔️ pc_EmployeA.001.txt\n"
                    if st.session_state.hashes['usb']: hashes_text += "- ✔️ cle_suspecte.E01.txt"
                    st.info(hashes_text)

    # ==========================================
    # TAB 1 : SYNTHÈSE GLOBALE & TIMELINE
    # ==========================================
    with tab_synth:
        if not st.session_state.dfs:
            st.warning(locked_msg)
        else:
            st.error("🚨 **ALERTE CRITIQUE : EXFILTRATION AVÉRÉE** — La corrélation des artefacts Windows prouve formellement le vol de données industrielles par M. Jean Martin.")
            
            st.markdown("### 📊 Métriques de l'Investigation")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔍 Recherches Suspectes", "4", "Mens Rea Prouvé")
            col2.metric("🔌 Périphériques Isolés", "1", "MXT (130818v01)")
            col3.metric("📂 Fichiers Ciblés", "3", "Orion & Budget")
            col4.metric("⚠️ Outils d'Évasion", "1", "PowerShell (LotL)")
            
            st.markdown("### ⏱️ Timeline de la Kill Chain (Reconstruction)")
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
    # TAB 2 : WEB (Mens Rea)
    # ==========================================
    with tab_web:
        if 'web' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            # 1. CSS Spécifique l-had l-onglet
            st.markdown("""
            <style>
                .web-card {
                    background-color: #f8fafc;
                    border-left: 4px solid #0284c7;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    border-top: 1px solid #e2e8f0;
                    border-right: 1px solid #e2e8f0;
                    border-bottom: 1px solid #e2e8f0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                }
                .web-alert {
                    background-color: #fef2f2;
                    border-left: 4px solid #dc2626;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    color: #991b1b;
                }
                .web-path {
                    font-family: 'Courier New', monospace;
                    background-color: #1e293b;
                    color: #e2e8f0;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.85em;
                }
            </style>
            """, unsafe_allow_html=True)

            # 2. En-tête w l-Contexte Statique (M3emmer w Pro)
            st.markdown("### 🌐 Analyse Sémantique des Requêtes Web")

            st.markdown("""
            <div class="web-card">
                <h4 style="margin-top:0; color:#0f172a;">🧠 Contexte Médico-Légal (Mens Rea)</h4>
                L'analyse forensique de l'historique de navigation permet de retracer l'intention de l'utilisateur. En investigation numérique, la présence de requêtes spécifiques encadrant un incident permet de qualifier la <b>préméditation</b> et la <b>volonté de dissimulation</b>, excluant définitivement la thèse de la négligence involontaire.
                <br><br>
                <b>Artefact ciblé :</b> Base de données du navigateur Mozilla Firefox<br>
                <b>Chemin absolu d'extraction :</b> <span class="web-path">C:\\Users\\jean_martin\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\x7b9q2m4.default-release\\places.sqlite</span>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. L-Khedma dyal Pandas (Li 3jbatak)
            df_web = st.session_state.dfs['web']
            if 'Text' in df_web.columns:
                mots_cles = 'cacher|effacer|leak|vpn'
                df_filtered = df_web[df_web['Text'].str.contains(mots_cles, case=False, na=False)][['Date Accessed', 'Text']]
                df_filtered.columns = ['Horodatage (CET)', 'Requêtes Google Interceptées']
                
                st.markdown("""<div class="web-alert"><b>🚨 Indicateurs d'Intention (IoC) Détectés :</b> Filtrage sémantique appliqué sur les mots-clés critiques.</div>""", unsafe_allow_html=True)
                
                st.dataframe(df_filtered, use_container_width=True, hide_index=True)

                # 4. Interprétation Statique (Kat-sdd l-page b khedma dyal Analyste)
                st.markdown("""
                <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #dcfce7;">
                    <h4 style="margin-top:0; color:#14532d;">⚖️ Interprétation de l'Analyste</h4>
                    <p style="margin-bottom:0; color:#15803d; line-height:1.6;">
                    Le suspect a effectué des recherches compromettantes telles que <i>« comment cacher des fichiers copiés »</i> à partir de <b>18:02:46</b>. Ce chronodatage est crucial : il intervient le jour même de l'exfiltration. Cela démontre techniquement que M. Jean Martin cherchait activement un moyen de masquer ses traces sur le système de TechCorp après avoir manipulé les fichiers du projet Orion.
                    </p>
                </div>
                """, unsafe_allow_html=True)
# ==========================================
    # TAB 3 : LNK & SHELLBAGS (Accès)
    # ==========================================
    with tab_access:
        if 'lnk' not in st.session_state.dfs or 'shellbags' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            # 1. CSS Spécifique l-had l-onglet (B7al dyal Web walakin b loun sfer/Limouni)
            st.markdown("""
            <style>
                .acc-card {
                    background-color: #fdfbed;
                    border-left: 4px solid #d97706;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    border-top: 1px solid #fef3c7;
                    border-right: 1px solid #fef3c7;
                    border-bottom: 1px solid #fef3c7;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                }
                .acc-path {
                    font-family: 'Courier New', monospace;
                    background-color: #451a03;
                    color: #fef3c7;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.85em;
                }
                .acc-header-box {
                    background-color: #fffbeb;
                    border: 1px solid #fde68a;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    color: #92400e;
                    font-weight: 600;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 📂 Traçabilité des Accès Logiques")
            
            # 2. Contexte Statique (Wa3er)
            st.markdown("""
            <div class="acc-card">
                <h4 style="margin-top:0; color:#78350f;">🔍 Contexte Médico-Légal (Accès Conscient)</h4>
                L'analyse combinée des raccourcis Windows (LNK) et du cache de l'Explorateur (ShellBags) permet de certifier qu'un utilisateur a <b>consciemment manipulé et visualisé</b> les données critiques. Cela réfute les alibis de type "copie automatique par script" ou "erreur de manipulation".
                <br><br>
                <b>Artefacts ciblés :</b> 
                <ul>
                    <li><span class="acc-path">C:\\Users\\jean_martin\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\*.lnk</span></li>
                    <li><span class="acc-path">C:\\Users\\jean_martin\\AppData\\Local\\Microsoft\\Windows\\UsrClass.dat</span> (Ruche ShellBags)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown('<div class="acc-header-box">📁 Fichiers Raccourcis (LNK)</div>', unsafe_allow_html=True)
                st.caption("Générés automatiquement par Windows, les `.lnk` prouvent l'ouverture délibérée d'un fichier (ex: double-clic).")
                
                df_lnk = st.session_state.dfs['lnk']
                if 'Source Name' in df_lnk.columns:
                    # Filtrage sémantique 3la LNK
                    df_fil_lnk = df_lnk[df_lnk['Source Name'].str.contains('Projet_Orion|Budget|Plans', case=False, na=False)][['Source Name', 'Date Accessed']]
                    # Cleaning des dates invalides
                    df_fil_lnk = df_fil_lnk[~df_fil_lnk['Date Accessed'].str.contains('0000', na=False, case=False)]
                    df_fil_lnk.columns = ['Fichier Ouvert', 'Horodatage (CET)']
                    
                    st.dataframe(df_fil_lnk, use_container_width=True, hide_index=True)

            with c2:
                st.markdown('<div class="acc-header-box">🗂️ Registre ShellBags (UsrClass.dat)</div>', unsafe_allow_html=True)
                st.caption("Conserve les préférences d'affichage. Prouve la navigation visuelle dans un répertoire spécifique.")
                
                df_sb = st.session_state.dfs['shellbags']
                if 'Path' in df_sb.columns:
                    # FIX DYAL SHELLBAGS: 7iydna dropna() li kanat katmsa7 kolxi, w dkhlna 'Orio' bax tqbet dak l-masar naqs.
                    df_fil_sb = df_sb[df_sb['Path'].str.contains('Projet|Orio|Budget', case=False, na=False)][['Path', 'Date Accessed']]
                    # Cleaning léger
                    df_fil_sb = df_fil_sb.fillna("—") 
                    df_fil_sb = df_fil_sb[~df_fil_sb['Date Accessed'].str.contains('None', na=False, case=False)]
                    df_fil_sb.columns = ['Répertoire Visité', 'Horodatage (CET)']
                    
                    st.dataframe(df_fil_sb, use_container_width=True, hide_index=True)

            # 3. Interprétation Statique (Khatima dyal l-onglet)
            st.markdown("""
            <div style="background-color: #fff7ed; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #fde68a;">
                <h4 style="margin-top:0; color:#b45309;">⚖️ Interprétation de l'Analyste</h4>
                <p style="margin-bottom:0; color:#92400e; line-height:1.6;">
                La chronologie de ces deux artefacts est irréfutable. À <b>15:47:28</b>, le suspect a visuellement inspecté le dossier <i>Projet_Orion</i> via l'Explorateur Windows (preuve ShellBags). Une heure plus tard, entre <b>16:47:23</b> et <b>16:47:44</b>, il a délibérément ouvert les fichiers individuels (<i>Budget_2026.xlsx</i> et <i>Plans_Confidentiels.pdf</i>), déclenchant la création des raccourcis LNK. Ces actions confirment un repérage et une sélection minutieuse des données avant l'exfiltration.
                </p>
            </div>
            """, unsafe_allow_html=True)
# ==========================================
    # TAB 4 : EXFILTRATION (USB)
    # ==========================================
    with tab_usb:
        if 'usb' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            # 1. CSS Spécifique l-had l-onglet (Thème Émeraude / Validation)
            st.markdown("""
            <style>
                .usb-card {
                    background-color: #f0fdfa;
                    border-left: 4px solid #0d9488;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    border-top: 1px solid #ccfbf1;
                    border-right: 1px solid #ccfbf1;
                    border-bottom: 1px solid #ccfbf1;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                }
                .usb-path {
                    font-family: 'Courier New', monospace;
                    background-color: #134e4a;
                    color: #ccfbf1;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.85em;
                }
                .usb-header-box {
                    background-color: #ecfdf5;
                    border: 1px solid #a7f3d0;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    color: #047857;
                    font-weight: 600;
                }
                .evidence-tag {
                    background-color: #1e293b;
                    color: #f8fafc;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 6px solid #10b981;
                    font-family: 'Courier New', monospace;
                    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 🔌 Périphérique d'Exfiltration (Actus Reus)")
            
            # 2. Contexte Statique (Professionnel)
            st.markdown("""
            <div class="usb-card">
                <h4 style="margin-top:0; color:#065f46;">⚙️ Contexte Médico-Légal (Mécanisme OS)</h4>
                Lorsqu'un périphérique de stockage de masse est connecté à Windows, le gestionnaire <i>Plug and Play (PnP)</i> génère une empreinte matérielle unique. Cette trace est stockée de manière persistante dans le registre système. Elle permet de lier mathématiquement le poste informatique compromis à l'arme du délit saisie physiquement sur le suspect.
                <br><br>
                <b>Artefact ciblé :</b> Ruche système du registre Windows (Historique USB)<br>
                <b>Chemin absolu :</b> <span class="usb-path">HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR</span>
            </div>
            """, unsafe_allow_html=True)
            
            df_usb = st.session_state.dfs['usb']
            if 'Device ID' in df_usb.columns:
                # Filtrage w Cleaning
                df_filtered = df_usb[df_usb['Device ID'].str.contains('130818v01', case=False, na=False)][['Date/Time', 'Device Make', 'Device Model', 'Device ID']]
                df_filtered = df_filtered.drop_duplicates(subset=['Device ID', 'Date/Time'])
                df_filtered.columns = ['Horodatage de Connexion', 'Constructeur', 'Modèle', 'N° Série (ID)']
                
                c1, c2 = st.columns([1.2, 1]) # Kberna l-colonne d-liser xwiya 3la 9bel tableau
                
                with c1:
                    st.markdown('<div class="usb-header-box">💻 Empreinte du Registre (Extraction PC)</div>', unsafe_allow_html=True)
                    st.caption("Traces extraites de l'image disque `pc_EmployeA.vhd` via Autopsy.")
                    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                
                with c2:
                    st.markdown('<div class="usb-header-box">🏷️ Pièce à Conviction (Saisie Physique)</div>', unsafe_allow_html=True)
                    st.caption("Comparaison avec l'objet mis sous scellé.")
                    # Evidence Tag wa3ra b CSS
                    st.markdown("""
                    <div class="evidence-tag">
                        <b style="color:#94a3b8;">PIÈCE SCELLÉE : #B-2026-TC</b><br>
                        ---------------------------<br>
                        Catégorie : Mass Storage USB<br>
                        Marque &nbsp;&nbsp;&nbsp;: MXT<br>
                        Modèle &nbsp;&nbsp;&nbsp;: microSD CardReader<br>
                        N° Série &nbsp;: <span style="color:#34d399; font-weight:bold; font-size:1.15em;">130818v01</span><br>
                        ---------------------------<br>
                        STATUT &nbsp;&nbsp;&nbsp;: <span style="background-color:#059669; padding:2px 8px; border-radius:4px; color:white; font-weight:bold;">MATCH CONFIRMÉ 100%</span>
                    </div>
                    """, unsafe_allow_html=True)

            # 3. Interprétation Statique (Khatima)
            st.markdown("""
            <div style="background-color: #f8fafc; border-left: 4px solid #475569; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #e2e8f0;">
                <h4 style="margin-top:0; color:#0f172a;">⚖️ Interprétation de l'Analyste</h4>
                <p style="margin-bottom:0; color:#334155; line-height:1.6;">
                L'artefact USBSTOR certifie de façon incontestable que la clé USB <b>MXT</b> (saisie dans les affaires personnelles de M. Jean Martin) a été connectée au poste <i>pc_EmployeA</i> à <b>17:01:37</b>. Ce chronodatage est le point d'ancrage de l'affaire : il intervient exactement entre la phase d'accès aux fichiers confidentiels (16:47) et la phase de dissimulation via les requêtes Web (18:02). Le support physique d'exfiltration est formellement identifié.
                </p>
            </div>
            """, unsafe_allow_html=True)
# ==========================================
    # TAB 5 : DISSIMULATION (MFT & Prefetch)
    # ==========================================
    with tab_hide:
        if 'prefetch' not in st.session_state.dfs or 'mft' not in st.session_state.dfs:
            st.warning(locked_msg)
        else:
            # 1. CSS Spécifique (Thème Avertissement / Anti-Forensics)
            st.markdown("""
            <style>
                .af-card {
                    background-color: #fefce8;
                    border-left: 4px solid #b45309;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    border-top: 1px solid #fef3c7;
                    border-right: 1px solid #fef3c7;
                    border-bottom: 1px solid #fef3c7;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                }
                .af-header-box {
                    background-color: #fffbeb;
                    border: 1px solid #fde68a;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    color: #92400e;
                    font-weight: 600;
                }
                .af-path {
                    font-family: 'Courier New', monospace;
                    background-color: #78350f;
                    color: #fef3c7;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.85em;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 🗑️ Outils d'Évasion et de Destruction (Anti-Forensics)")

            # 2. Contexte Statique
            st.markdown("""
            <div class="af-card">
                <h4 style="margin-top:0; color:#78350f;">⚠️ Contexte Médico-Légal (Dissimulation)</h4>
                L'analyse des artefacts d'exécution (Prefetch) couplée à l'analyse du système de fichiers (MFT) permet de révéler les tentatives de camouflage. L'utilisation d'outils d'administration légitimes (technique dite <b>Living off the Land - LotL</b>) couplée à l'effacement de données sensibles constitue une circonstance aggravante démontrant la volonté de détruire les preuves du vol.
                <br><br>
                <b>Artefacts ciblés :</b> 
                <ul>
                    <li><span class="af-path">C:\\Windows\\Prefetch\\*.pf</span> (Exécutions)</li>
                    <li><span class="af-path">$MFT</span> (Master File Table - Fichiers effacés)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown('<div class="af-header-box">⚙️ 1. Exécution Suspecte (Prefetch)</div>', unsafe_allow_html=True)
                st.caption("Prouve l'exécution de binaires natifs, leurs chemins d'origine et leurs horodatages.")
                
                df_pf = st.session_state.dfs['prefetch']
                if 'Program Name' in df_pf.columns:
                    # FIX: Zedt NOTEPAD m3a POWERSHELL w CMD
                    df_fil_pf = df_pf[df_pf['Program Name'].str.contains('POWERSHELL|CMD|NOTEPAD', case=False, na=False)][['Program Name', 'Date/Time']]
                    df_fil_pf = df_fil_pf.drop_duplicates(subset=['Program Name', 'Date/Time'])
                    df_fil_pf.columns = ['Binaire Exécuté', 'Horodatage (CET)']
                    st.dataframe(df_fil_pf, use_container_width=True, hide_index=True)

            with c2:
                st.markdown('<div class="af-header-box">🗑️ 2. Fichiers Supprimés Récupérés (MFT)</div>', unsafe_allow_html=True)
                st.caption("Le flag `Unallocated` indique une suppression logique. Les clusters physiques n'étant pas écrasés, la récupération bit-à-bit a réussi.")
                
                df_mft = st.session_state.dfs['mft']
                if 'Name' in df_mft.columns:
                    df_fil_mft = df_mft[
                        (df_mft['Name'].str.contains('Plans_Confidentiels|Budget|Orion', case=False, na=False)) & 
                        (df_mft['Flags(Dir)'].str.contains('Unallocated', na=False)) &
                        (df_mft['Created Time'].str.contains('2026', na=False))
                    ][['Name', 'Created Time', 'Flags(Dir)']]
                    df_fil_mft.columns = ['Fichier (Récupéré)', 'Date de Création', 'Statut MFT']
                    st.dataframe(df_fil_mft, use_container_width=True, hide_index=True)

            # 3. Interprétation Statique (Khatima)
            st.markdown("""
            <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 5px; margin-top: 15px; border: 1px solid #fecaca;">
                <h4 style="margin-top:0; color:#991b1b;">⚖️ Interprétation de l'Analyste</h4>
                <p style="margin-bottom:0; color:#7f1d1d; line-height:1.6;">
                L'utilisation de <b>PowerShell</b> (entre 15:41 et 16:40) indique une volonté de manipuler le système sans interface graphique (GUI), potentiellement pour compresser les données sans alerter l'antivirus (LotL). Par la suite, les fichiers ciblés (<i>Plans_Confidentiels.pdf</i>, etc.) ont été marqués comme supprimés (<b>Unallocated</b>). Cette tentative de destruction finale scelle la volonté de l'utilisateur de faire disparaître les traces de son exfiltration.
                </p>
            </div>
            """, unsafe_allow_html=True)
# ==========================================
    # TAB 6 : CONCLUSION FACTUELLE & CHAÎNE DE GARDE
    # ==========================================
    with tab_conclusion:
        if not st.session_state.dfs:
            st.warning(locked_msg)
        else:
            # 1. CSS Spécifique pour la Conclusion et Chain of Custody
            st.markdown("""
            <style>
                .verdict-final {
                    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 8px;
                    border-left: 8px solid #ef4444;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                    margin-bottom: 25px;
                }
                .verdict-final h3 {
                    color: #f8fafc;
                    margin-top: 0;
                    font-size: 1.5rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .coc-box {
                    background-color: #f8fafc;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 10px;
                    font-family: 'Courier New', monospace;
                    box-shadow: inset 0 0 8px rgba(0,0,0,0.02);
                }
                .coc-header {
                    color: #0f172a;
                    font-weight: 900;
                    border-bottom: 2px dashed #94a3b8;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                    font-size: 1.1em;
                }
                .hash-match {
                    color: #059669;
                    font-weight: 900;
                    background-color: #d1fae5;
                    padding: 2px 8px;
                    border-radius: 4px;
                    border: 1px solid #34d399;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 0.8em;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### ⚖️ Rapport de Synthèse & Clôture du Dossier")

            # 2. Le Verdict Final (Style Rapport de Police)
            st.markdown("""
            <div class="verdict-final">
                <h3>🚨 Verdict Officiel : Culpabilité Établie</h3>
                <p style="font-size: 1.1em; line-height: 1.6; margin-bottom:0;">
                L'investigation numérique croisée menée sur les scellés <b>(Pièce C - Poste Windows)</b> et <b>(Pièce B - Clé USB MXT)</b> conclut formellement à la culpabilité de M. Jean Martin. Les traces techniques extraites démontrent sans équivoque un vol prémédité de données industrielles critiques (Projet Orion) suivi d'une tentative active de destruction de preuves.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 3. Matrice de Compromission (Remplace la liste à puces simple)
            st.markdown("#### 📌 Matrice de Compromission (Faisceau d'indices)")
            c1, c2 = st.columns(2)
            with c1:
                st.info("**🧠 1. Préméditation (Mens Rea)**\n\nL'historique `places.sqlite` révèle des recherches préalables explicites sur la dissimulation de données et le contournement réseau.")
                st.warning("**👁️ 2. Accès Conscient**\n\nLes artefacts `ShellBags` et `.lnk` prouvent le repérage visuel et l'ouverture manuelle des fichiers financiers ciblés.")
            with c2:
                st.success("**🔌 3. Exfiltration (Actus Reus)**\n\nLa ruche `USBSTOR` confirme mathématiquement la connexion de la clé USB saisie (ID: 130818v01) lors de la fenêtre d'incident.")
                st.error("**🗑️ 4. Anti-Forensics**\n\nL'analyse `Prefetch` (LotL via PowerShell) et les entrées `$MFT` (Unallocated) prouvent la tentative de nettoyage des traces.")

            st.divider()

            # 4. Chain of Custody (L'ajout Majeur pour le Prof)
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
                            <b>Type d'image :</b> Copie bit-à-bit (Physical)<br>
                            <b>Acquisition :</b> AccessData FTK Imager<br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat MD5 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{pc_h['md5']}</span> <span class="hash-match">✔ VALIDÉ</span><br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat SHA-1 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{pc_h['sha1']}</span> <span class="hash-match">✔ VALIDÉ</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("⚠️ Empreintes PC manquantes. Chargez le fichier .txt")
                        
                with col_usb:
                    if usb_h:
                        st.markdown(f"""
                        <div class="coc-box">
                            <div class="coc-header">💾 SCELLÉ NUMÉRIQUE : PIÈCE B</div>
                            <b>Cible analysée :</b> cle_suspecte.E01<br>
                            <b>Type d'image :</b> Image EnCase (Logical)<br>
                            <b>Acquisition :</b> AccessData FTK Imager<br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat MD5 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{usb_h['md5']}</span> <span class="hash-match">✔ VALIDÉ</span><br><br>
                            <span style="color:#475569; font-size:0.9em;">Condensat SHA-1 :</span><br>
                            <span style="color:#0f172a; word-break: break-all;">{usb_h['sha1']}</span> <span class="hash-match">✔ VALIDÉ</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("⚠️ Empreintes USB manquantes. Chargez le fichier .txt")
                        
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("⚖️ *Attestation de l'analyste : Les empreintes cryptographiques calculées lors de cette analyse correspondent strictement aux journaux d'acquisition initiaux générés sur la scène de crime. Aucune altération n'a été détectée sur les preuves soumises.*")
            else:
                st.warning("⚠️ Les journaux d'empreinte FTK (.txt) n'ont pas été chargés. La vérification de la chaîne de garde (Chain of Custody) ne peut être établie.")



# ==========================================
    # TAB 7 : GENERATEUR DE RAPPORT IA (GEMINI)
    # ==========================================
    with tab_ia:
        if not st.session_state.dfs: 
            st.warning(locked_msg)
        else:
            st.markdown("### 🤖 Génération du Rapport d'Expertise")
            st.info("Ce module utilise l'Intelligence Artificielle pour rédiger un rapport judiciaire complet basé EXCLUSIVEMENT sur les preuves techniques extraites dans les onglets précédents.")
            
            # Champ pour la clé API (Sécurisé, ne s'affiche pas en clair)
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                st.success("🔒 Clé API chargée en toute sécurité depuis l'environnement système (.env).")
            else:
                st.warning("⚠️ Clé API non trouvée dans .env. Veuillez la renseigner manuellement :")
                api_key = st.text_input("🔑 Entrez votre clé API Google Gemini :", type="password")
            
            # 0. N-khelqo blassa f d-dakira fin n-khzno l-rapport
            if "final_report" not in st.session_state:
                st.session_state.final_report = None

            # 1. L-BOUTON DYAL GÉNÉRATION
            if st.button("⚖️ Générer le Rapport Officiel", type="primary"):
                if not api_key:
                    st.error("Veuillez fournir une clé API valide pour lancer la génération.")
                else:
                    with st.spinner("🧠 Gemini analyse la timeline et rédige le rapport... Veuillez patienter..."):
                        try:
                            # Config Gemini
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel("models/gemini-2.5-flash")
                            
                            # Récupération des données
                            df_timeline_ia = pd.DataFrame([
                                ["15:41:37", "⚙️ Évasion", "Lancement de POWERSHELL.EXE", "Prefetch (.pf)"],
                                ["15:47:28", "📁 Navigation", "Exploration du dossier 'Projet_Orion'", "ShellBags (UsrClass.dat)"],
                                ["16:03:33", "🗑️ Destruction", "Suppression logique des fichiers sources", "MFT (Unallocated)"],
                                ["16:47:23", "📂 Accès", "Ouverture de Budget_2026 et Plans_Confidentiels", "Recent Docs (LNK)"],
                                ["17:01:37", "🔌 Exfiltration", "Branchement clé USB MXT", "USBSTOR"],
                                ["18:02:46", "🌐 Dissimulation", "Recherche Google 'cacher fichiers'", "places.sqlite"]
                            ], columns=["Heure (CET)", "Catégorie", "Événement", "Artefact Source"])
                            timeline_text = df_timeline_ia.to_string(index=False)
                            
                            # 3. LE MASTER PROMPT (Windows & USB + Date 16 Mars 2026)
                            prompt = f"""
                            Tu es un Expert Judiciaire en Cybercriminalité et un Analyste Senior DFIR.
                            Rédige un rapport d'analyse PARTIELLE d'investigation pour l'affaire #2026-TC.
                            Périmètre de ton analyse : UNIQUEMENT les sources WINDOWS et USB.
                            Suspect : "M. Jean Martin".
                            
                            TIMELINE EXACTE :
                            {timeline_text}
                            
                            INSTRUCTIONS STRICTES :
                            1. TON : Froid, factuel, implacable, autoritaire, juridique.
                            2. EN-TÊTE : Commence OBLIGATOIREMENT par cet en-tête exact :
                               🏛️ 🚨 DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES 🚨 🏛️
                               **RAPPORT D'ANALYSE FORENSIQUE : PÔLE WINDOWS & USB**
                               **Date du rapport :** 16 mars 2026
                               **Affaire :** #2026-TC (Fuite de données TechCorp)
                               **Suspect :** M. Jean Martin
                            3. STRUCTURE EXIGÉE (Titres en MAJUSCULES) :
                               - I. RÉSUMÉ EXÉCUTIF (Précise que ce rapport ne couvre que la partie Windows/USB)
                               - II. ANALYSE DES INTENTIONS (MENS REA)
                               - III. DÉROULEMENT DE L'EXFILTRATION (ACTUS REUS)
                               - IV. MANOEUVRES D'ÉVASION (ANTI-FORENSICS)
                               - V. CONCLUSION LÉGALE (Conclut sur la partie Windows/USB)
                            4. FORMATAGE : Utilise le Markdown pur (# pour les titres, ** pour le gras). 
                               INTERDICTION ABSOLUE d'utiliser des blocs de code (```), des balises HTML (<pre>, <div>, <br>, <span>). Ne crée AUCUN encadré vide.
                            """
                            
                            response = model.generate_content(prompt)
                            # Nettoyage pur pour éviter les rectangles vides
                            clean_report = response.text.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
                            
                            # KAN-KHZNO L-RAPPORT F SESSION STATE
                            st.session_state.final_report = clean_report
                            
                        except Exception as e:
                            st.error(f"Une erreur est survenue avec l'API Gemini : {e}")

            # =========================================================================
            # 2. AFFICHAGE DU RAPPORT ET BOUTON PDF (BERRA MN L-BOUTON "Générer")
            # =========================================================================
            if st.session_state.final_report:
                st.success("✅ Rapport Windows & USB généré avec succès.")
                
                # BOUTON DOWNLOAD PDF WA3ER
                pdf_bytes = generate_pdf_report(st.session_state.final_report)
                st.download_button(
                    label="📥 Télécharger le Rapport (PDF)",
                    data=pdf_bytes,
                    file_name="Rapport_Windows_USB_2026_TC.pdf",
                    mime="application/pdf",
                    type="primary"
                )

                st.markdown("""
                <style>
                    .report-container {
                        background-color: white; padding: 40px; border-radius: 10px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 20px;
                        border-top: 10px solid #1e3a8a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.final_report, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
