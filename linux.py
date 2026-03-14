import streamlit as st
import pandas as pd

def run_linux_forensics():
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <h1 style="margin:0; color:#065F46;">🐧 Pôle d'Analyse : Serveur Linux</h1>
    </div>
    <p style="font-size:14px; color:gray;"><b>Analyste :</b> Ismail | <b>Cible :</b> SRV-WEB-01 | <b>Outils :</b> Bash Logs, Auth.log, Apache Logs</p>
    <hr style="margin-top:0px; margin-bottom:20px;">
    """, unsafe_allow_html=True)

    tab_logs, tab_auth, tab_bash = st.tabs(["📄 Web Logs", "🔐 Authentification", "⌨️ Bash History"])
    
    with tab_logs:
        st.info("Espace pour l'analyse des logs Apache/Nginx...")
        # Hna Ismail ghadi y-zid l-code dyal pandas li kayqra les logs
        
    with tab_auth:
        st.info("Espace pour les attaques Bruteforce (auth.log)...")

    with tab_bash:
        st.info("Espace pour les commandes tapées par le hacker (.bash_history)...")