import streamlit as st

# Kan-importiw l-fichiers dyal l-equipe kamla
import windows_usb_zakaria
import linux_pcap
import mobile_nlp

# Configuration dyal la page
st.set_page_config(page_title="Forensic Dashboard - TechCorp", page_icon="🛡️", layout="wide")

# L-Menu f jjenb (Sidebar)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/FBI_seal.svg/200px-FBI_seal.svg.png", width=100)
st.sidebar.title("Menu Investigation")

# Hna zedna les 3 parties f l-menu
page = st.sidebar.radio("Navigation", [
    "🏠 Accueil", 
    "💻 Windows & USB (Zakaria)", 
    "🐧 Serveur Linux & Réseau (PCAP)",
    "📱 Investigation Mobile & NLP"
])

# L-Khedma dyal l-Menu
if page == "🏠 Accueil":
    st.title("🛡️ Dashboard Officiel - Affaire TechCorp")
    st.warning("🚨 **VERDICT OFFICIEL : EXFILTRATION AVÉRÉE**")
    st.write("Bienvenue sur le tableau de bord interactif de l'investigation numérique.")
    st.write("L'analyse stricte des supports numériques conclut formellement à la culpabilité de M. Jean Martin pour vol de données industrielles et tentative de destruction de preuves.")

elif page == "💻 Windows & USB (Zakaria)":
    # L-Partie dyalk (Deja 3ndk fiha l-code)
    windows_usb_zakaria.run()

elif page == "🐧 Serveur Linux & Réseau (PCAP)":
    # L-Partie dyal sa7bek 1
    linux_pcap.run()

elif page == "📱 Investigation Mobile & NLP":
    # L-Partie dyal sa7bek 2 (Dri 3)
    mobile_nlp.run()
