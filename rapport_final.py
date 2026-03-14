import streamlit as st


def run():
    # En-tête dyal l-page
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <h1 style="margin:0; color:#1E3A8A;">📜 Générateur du Rapport Final (Global)</h1>
    </div>
    <p style="font-size:14px; color:gray;"><b>Équipe :</b> DFIR Complete Team | <b>Affaire :</b> #2026-TC</p>
    <hr style="margin-top:0px; margin-bottom:20px;">
    """, unsafe_allow_html=True)

    # Message d'information
    st.info("💡 Cette section consolidera automatiquement les analyses de tous les pôles (Windows, Linux, Réseau, Mobile) pour générer le rapport juridique final.")

    # L-Bouton li glti (b-ghayr fa3al daba)
    if st.button("⚖️ Générer le Rapport Global", type="primary"):
        st.warning("⚠️ Module en cours de construction. En attente de l'intégration des données de tous les membres de l'équipe.")