import streamlit as st
from streamlit_option_menu import option_menu

# 1. Configuration de la page (Toujours en premier dans Streamlit)
st.set_page_config(page_title="C.I.A.F. - Investigation", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# 2. CUSTOM CSS (Design Light Mode Officiel & Professionnel)
st.markdown("""
<style>
    /* Titre Principal de la plateforme */
    .cyber-title {
        font-size: 3.2rem;
        color: #0F172A;
        font-weight: 900;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0px;
        border-bottom: 4px solid #1E3A8A;
        padding-bottom: 10px;
    }
    
    /* Sous-titre façon terminal */
    .cyber-subtitle {
        color: #475569;
        font-size: 1.15rem;
        margin-top: 15px;
        font-family: 'Courier New', Courier, monospace;
        background-color: #F8FAFC;
        padding: 10px;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
    }

    /* Boîte de Verdict (Alerte Rouge) */
    .verdict-box {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 20px;
        border-radius: 8px;
        border-left: 8px solid #DC2626;
        border-right: 1px solid #FECACA;
        font-weight: 900;
        text-align: center;
        font-size: 1.6rem;
        letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(220, 38, 38, 0.15);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(220, 38, 38, 0.1); }
        50% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.3); }
        100% { box-shadow: 0 0 10px rgba(220, 38, 38, 0.1); }
    }

    /* Cartes des pôles d'analyse */
    .info-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #1E3A8A;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(30, 58, 138, 0.15);
        border-top: 4px solid #DC2626;
    }

    .info-card h4 {
        color: #0F172A;
        font-weight: bold;
        margin-top: 0;
    }
    
    .info-card p {
        color: #475569;
        font-family: monospace;
    }
    
    .info-card ul {
        color: #334155;
        font-size: 0.95rem;
    }

    /* Styling des KPIs (Metrics) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1E3A8A;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# 3. MENU LATÉRAL (SIDEBAR) - MISE EN VALEUR DE C.I.A.F.
with st.sidebar:
    st.markdown("### 🛡️ **Plateforme C.I.A.F.**")
    st.caption("**C**onsole **I**nteractive d'**A**nalyse **F**orensique")
    
    st.markdown("""
    ---
    **📋 Fiche de l'Enquête :**
    * **Affaire :** TechCorp
    * **Projet compromis :** *Orion*
    * **Date d'acquisition :** 21 Fév 2026
    ---
    """)
    
    st.success("✅ **Environnement Isolé & Sécurisé**")
    st.divider()
    
    # ======== NAVIGATION ========
    page = option_menu(
        menu_title="MENU C.I.A.F.",
        options=["Dashboard", "Windows & USB", "Serveur Linux & PCAP", "Mobile & NLP (IA)", "Rapport Final"], 
        icons=["cpu", "windows", "terminal", "phone", "journal-check"],
        menu_icon="shield-lock",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#1E3A8A", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"5px", "color": "#0F172A", "font-family": "monospace"},
            "nav-link-selected": {"background-color": "#1E3A8A", "color": "white", "font-weight": "bold"},
        }
    )
    st.divider()
    st.caption("© 2026 EST - C.I.A.F. DFIR Team")

# ==========================================
# 4. GESTION DES PAGES (ROUTING)
# ==========================================

if page == "Dashboard":
    # En-tête avec le nom officiel
    st.markdown('<div class="cyber-title">C.I.A.F. - TABLEAU DE BORD</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cyber-subtitle">
        >> Initialisation de la Console Interactive d'Analyse Forensique (C.I.A.F.)... Terminé.<br>
        >> Synchronisation des pôles d'investigation... OK.<br>
        >> Cible en cours d'analyse : Infrastructure TechCorp (Affaire Orion).
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # L-KPIs (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🔍 Artefacts Détectés", value="14", delta="MFT, LNK, Registre")
    with col2:
        st.metric(label="💾 Périphériques Isolés", value="3", delta="PC, USB, Mobile", delta_color="off")
    with col3:
        st.metric(label="⚠️ Niveau d'Alerte", value="CRITIQUE", delta="Fuite Confirmée", delta_color="inverse")
    with col4:
        st.metric(label="⏱️ Temps de Réponse", value="48h", delta="SLA Respecté", delta_color="normal")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # L-Verdict
    st.markdown('<div class="verdict-box">>> ALERTE : EXFILTRATION DE DONNÉES AVÉRÉE <<</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Répartition des tâches
    st.markdown("### 🏛️ UNITÉS D'INTERVENTION C.I.A.F.")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="info-card">
            <h4>💻 Pôle Windows & USB</h4>
            <p><b>Opérateur :</b> Zakaria</p>
            <ul>
                <li>Analyse du registre (USBSTOR)</li>
                <li>Récupération MFT (Fichiers effacés)</li>
                <li>Historique Web & Mens Rea</li>
                <li>Traces d'exécution (Prefetch/LotL)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="info-card">
            <h4>🐧 Pôle Réseau & Linux</h4>
            <p><b>Opérateur :</b> Ismail</p>
            <ul>
                <li>Analyse des trames réseau (PCAP)</li>
                <li>Audit des logs du serveur cible</li>
                <li>Détection des connexions C2</li>
                <li>Traçabilité des adresses IP</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="info-card">
            <h4>📱 Pôle Mobile & IA (NLP)</h4>
            <p><b>Opérateur :</b> Ahmed</p>
            <ul>
                <li>Extraction physique du smartphone</li>
                <li>Modèle IA (NLP) sur les SMS</li>
                <li>Géolocalisation du suspect</li>
                <li>Analyse des applications tierces</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif page == "Windows & USB":
    import windows_usb_zakaria
    windows_usb_zakaria.run()

elif page == "Serveur Linux & PCAP":
    tab_linux, tab_pcap = st.tabs(["🐧 Analyse Serveur Linux", "📡 Analyse Trafic Réseau (PCAP)"])
    
    with tab_linux:
        try:
            import linux
            linux.run()
        except Exception as e:
            st.info("⚠️ Le module Linux de la plateforme C.I.A.F. est en cours de développement par Ismail.")
            
    with tab_pcap:
        try:
            import pcap
            pcap.run()
        except Exception as e:
            st.info("⚠️ Le module PCAP de la plateforme C.I.A.F. est en cours de développement par Ismail.")

elif page == "Mobile & NLP (IA)":
    try:
        import mobile_nlp
        mobile_nlp.run()
    except Exception as e:
        st.info("⚠️ Le module Mobile de la plateforme C.I.A.F. est en cours de développement par Ahmed.")

elif page == "Rapport Final":
    try:
        import rapport_final
        rapport_final.run()
    except Exception as e:
        st.error(f"Erreur dans le module de génération de rapport C.I.A.F. : {e}")