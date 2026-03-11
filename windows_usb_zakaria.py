import streamlit as st
import os

# Fonction Pro bax t-chargi tsawer bla may-planta l-app
def load_safe_image(image_name, caption_text):
    # Kay-jib l-chemin exact dyal l-dossier fin kayn had l-fichier
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "assets", image_name)
    
    # Kay-cheki wax tswira kayna b sse7
    if os.path.exists(image_path):
        st.image(image_path, caption=caption_text)
    else:
        st.warning(f"⚠️ Image introuvable : `assets/{image_name}`. T2ked mn smya wla l-extension (.png/.jpg)")

def run():
    # 1. En-tête de la page
    st.markdown("## 💻 Pôle d'Analyse : Environnement Windows & Périphériques")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.info("🧑‍💻 **Analyste DFIR :** Zakaria")
    col_b.info("🎯 **Cible :** `pc_EmployeA.vhd` (Jean Martin)")
    col_c.info("🛠️ **Outils :** Autopsy 4.22.1 & FTK Imager")
    st.markdown("---")

    # 2. Les Onglets de Preuves
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🌐 1. Web", 
        "🔌 2. USB", 
        "📂 3. LNK", 
        "📁 4. ShellBags",
        "🗑️ 5. MFT", 
        "⚙️ 6. Prefetch",
        "📝 RAPPORT"
    ])

    # ==========================================
    # TAB 1 : HISTORIQUE WEB
    # ==========================================
    with tab1:
        st.subheader("1. Preuve formelle de préméditation (Mens Rea)")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Base de données `places.sqlite` (Navigateur Firefox).")
            st.code("Chemin Autopsy : Data Artifacts > Web History")
            
            st.markdown("🔍 **Extraction des requêtes exactes :**")
            st.markdown("""
            | Date Accessed (CET) | Requête / Titre | Source |
            | :--- | :--- | :--- |
            | 2026-02-21 18:02:46 | *comment cacher des fichiers copiés* | Firefox |
            | 2026-02-21 18:03:19 | *Comment effacer définitivement...* | Firefox |
            | 2026-02-21 18:03:54 | *techcorp data leak* | Firefox |
            | 2026-02-21 18:04:35 | *vpn - Recherche Google* | Firefox |
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("Le timing de ces recherches démontre techniquement **l'intention coupable (Mens Rea)** de Jean Martin. Le suspect a planifié la fuite de données et cherché des moyens de dissimuler ses traces.")
        
        with c2:
            # Jrebna n-3eyto l .jpg, ila mal9ahax aytl3 lik l-msg d'erreur sfer
            load_safe_image("web_history_autopsy.png", "Extraction des requêtes depuis places.sqlite")
            # Ila knt tswira 3ndk b .png, bdleha hna l-te7t w msa7 li l-fo9:
            # load_safe_image("web_history_autopsy.png", "Extraction des requêtes depuis places.sqlite")

    # ==========================================
    # TAB 2 : CONNEXION USB
    # ==========================================
    with tab2:
        st.subheader("2. Traçabilité du Périphérique de Stockage")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Historique de connexion USB via le registre Windows.")
            st.code("Chemin : Data Artifacts > USB Device Attached \nSource : /Windows/System32/config/SYSTEM (Ruche USBSTOR)")
            
            st.markdown("🔍 **Données extraites du Registre :**")
            st.success("""
            * **Date/Time :** 2026-02-21 17:01:37 CET
            * **Device Make :** MXT
            * **Device Model :** microSD CardReader
            * **Device ID (Serial) :** 130818v01
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("L'artefact USBSTOR lie formellement le poste de travail à l'arme du délit. La clé USB saisie correspond exactement au Device ID `130818v01` connecté le jour de l'incident.")
            
        with c2:
            load_safe_image("preuve_usb_autopsy.png", "Artefact USBSTOR dans Autopsy")

    # ==========================================
    # TAB 3 : FICHIERS RECENTS (LNK)
    # ==========================================
    with tab3:
        st.subheader("3. Preuve d'accès interactif aux données (LNK)")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Fichiers raccourcis (.lnk) générés par Windows.")
            st.code("Chemin : Data Artifacts > Recent Documents")
            
            st.markdown("🔍 **Traces d'accès aux fichiers critiques :**")
            st.markdown("""
            | Fichier Source | Date Accessed (CET) | Chemin d'origine |
            | :--- | :--- | :--- |
            | **Projet_Orion.lnk** | 2026-02-21 16:47:23 | `C:\\...\\Projet_Orion` |
            | **Budget_2026.xlsx.lnk** | 2026-02-21 16:47:44 | `C:\\...\\Budget_2026.xlsx` |
            | **Plans_Confidentiels.pdf.lnk** | 2026-02-21 16:47:32 | `C:\\...\\Plans_Confidentiels.pdf` |
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("Ces traces d'accès consécutives réfutent totalement la thèse d'une copie accidentelle.")
            
        with c2:
            load_safe_image("recent_documents.png", "Traces d'ouverture des fichiers ciblés (LNK)")

    # ==========================================
    # TAB 4 : SHELLBAGS (NAVIGATION)
    # ==========================================
    with tab4:
        st.subheader("4. Exploration des répertoires (ShellBags)")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Préférences d'affichage de l'Explorateur Windows.")
            st.code("Chemin : Data Artifacts > Shell Bags \nSource : UsrClass.dat")
            
            st.markdown("🔍 **Traces de navigation :**")
            st.warning("""
            * **Path Navigué :** `Explorer\\Projet_Orion`
            * **Date Accessed :** 2026-02-21 15:47:28 CET
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("Prouve que Jean Martin a navigué et inspecté visuellement le dossier contenant les données confidentielles.")
            
        with c2:
            load_safe_image("shellbags_autopsy.png", "Traces de navigation (ShellBags)")

    # ==========================================
    # TAB 5 : MFT & RECUPERATION
    # ==========================================
    with tab5:
        st.subheader("5. Tentative de dissimulation et Récupération MFT")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Entrées de la Master File Table (MFT).")
            st.code("Chemin : Deleted Files > File System")
            
            st.markdown("🔍 **État du fichier cible :**")
            st.error("""
            * **Nom du Fichier :** `Plans_Confidentiels.pdf`
            * **Statut MFT :** `Unallocated`
            * **Created Time :** 2026-02-21 16:03:33 CET
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("Le suspect a vidé la corbeille. Cependant, il s'agissait d'une simple suppression logique. Les clusters physiques n'ayant pas été écrasés, nous avons récupéré l'aperçu natif.")
            
        with c2:
            load_safe_image("recuperation_pdf.png", "Fichier marqué Unallocated récupéré via MFT")

    # ==========================================
    # TAB 6 : PREFETCH (LotL)
    # ==========================================
    with tab6:
        st.subheader("6. Exécution d'outils système (Living off the Land)")
        c1, c2 = st.columns([0.5, 0.5])
        
        with c1:
            st.markdown("**Artefact ciblé :** Fichiers d'optimisation d'exécution.")
            st.code("Chemin : Data Artifacts > Run Programs \nExtensions : .pf")
            
            st.markdown("🔍 **Exécutions suspectes :**")
            st.warning("""
            * **Program Name :** `POWERSHELL.EXE`
            * **Horodatage :** 2026-02-21 15:41:37 CET
            * **Count :** 3 exécutions
            """)
            
            st.markdown("⚖️ **Analyse Forensique :**")
            st.write("Prouve l'utilisation de PowerShell (*Living off the Land*) pour contourner les alertes de l'antivirus lors de la manipulation.")
            
        with c2:
            load_safe_image("prefetch_autopsy.png", "Traces Prefetch de l'exécution de PowerShell")

    # ==========================================
    # TAB 7 : RAPPORT FINAL
    # ==========================================
    with tab7:
        st.subheader("📑 Rapport de Synthèse Légal et Technique")
        
        st.markdown("""
        <div style="background-color: #fee2e2; color: #991b1b; padding: 20px; border-radius: 5px; border-left: 5px solid #dc2626; margin-bottom: 20px;">
            <h4 style="margin-top:0px; color: #991b1b;">VERDICT OFFICIEL : EXFILTRATION AVÉRÉE</h4>
            Les artefacts collectés prouvent de manière irréfutable le vol prémédité de données industrielles.
        </div>
        """, unsafe_allow_html=True)
        
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            st.markdown("### ⛓️ Kill Chain")
            st.markdown("""
            1. **Préméditation (Mens Rea) :** Recherches Google pour cacher son vol (`places.sqlite`).
            2. **Accès Conscient :** Interaction avec les fichiers (`.lnk`).
            3. **Exfiltration (Actus Reus) :** Connexion de la clé USB (`USBSTOR`).
            4. **Évasion :** Utilisation de PowerShell (`Prefetch`) et destruction (`MFT Unallocated`).
            """)
            
        with col_sum2:
            st.markdown("### 🔒 Chaîne de Garde (Hashes)")
            with st.expander("Voir les empreintes cryptographiques", expanded=True):
                st.code("""
[Image système PC : pc_EmployeA.001]
MD5  : 44df1a6c80c4442637162ce6ea35d987

[Image clé USB : cle_suspecte.E01]
MD5  : 7e3eba77127fed91102a10e94b2b6757
                """)