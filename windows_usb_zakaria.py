import streamlit as st
import os

def run():
    st.title("💻 Analyse Forensique : Poste Windows & Clé USB")
    st.markdown("**Examinateur :** Zakaria  |  **Outil :** Autopsy & FTK Imager")
    st.markdown("---")

    # Khelq 4 dyal les Onglets (Tabs)
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 Historique Web (Mens Rea)", "🔌 Traçabilité USB", "🗑️ Fichiers Supprimés", "⚙️ Programmes Exécutés"])

    with tab1:
        st.subheader("Preuve formelle de préméditation (Mens Rea)")
        st.write("**Artefact ciblé :** Base de données `places.sqlite` (Firefox).")
        st.info("📌 **Requêtes trouvées :** 'comment cacher des fichiers copiés', 'techcorp data leak'")
        st.write("La corrélation est parfaite. L'intention de dissimuler le vol est prouvée techniquement.")
        # Ila 3ndk tswira f dossier assets smytha web.png, 7iyd had l-# w tkhdem:
        # st.image("assets/web_history_autopsy.png", caption="Extraction de l'historique Web")

    with tab2:
        st.subheader("Preuve de connexion du support externe")
        st.write("**Artefact ciblé :** Clé de registre `SYSTEM` (ruche `USBSTOR`).")
        st.success("✅ **Corrélation :** Le numéro de série trouvé dans le PC correspond à la clé saisie : **130818v01**")
        # st.image("assets/preuve_usb_autopsy.png", caption="USB Device Attached")

    with tab3:
        st.subheader("Analyse de la Master File Table (MFT)")
        st.write("Malgré le vidage de la corbeille, le fichier a été retrouvé.")
        st.warning("⚠️ **Localisation :** Dossier `Deleted Files`. Fichier marqué `Unallocated`.")
        st.write("Le système a supprimé l'entrée MFT, mais les clusters de données n'ont pas été écrasés.")
        # st.image("assets/recuperation_pdf.png", caption="Fichier Plans_Confidentiels.pdf")

    with tab4:
        st.subheader("Traces d'exécution des outils système")
        st.write("**Artefact ciblé :** Fichiers Prefetch (`.pf`).")
        st.error("🚨 Exécution répétée de `POWERSHELL.EXE` (Count: 3).")
        st.write("Confirme l'utilisation d'outils en ligne de commande (Living off the Land) pour manipuler les données.")
        # st.image("assets/prefetch_autopsy.png", caption="Run Programs (Autopsy)")
