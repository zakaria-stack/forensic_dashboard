# =============================================================================
# MODULE PCAP — Pôle Réseau & Analyse Trafic
# Analyste : Ismail
# Affaire  : TechCorp #2026-TC — Suspicion d'exfiltration via FTP
# Outils   : Scapy, Streamlit, Gemini 2.5 Flash
# =============================================================================

import streamlit as st
import pandas as pd
import os
import hashlib
import tempfile
import time
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

from fpdf import FPDF
import google.generativeai as genai

# =============================================================================
# GÉNÉRATION PDF (Même pattern que windows_usb_zakaria.py)
# =============================================================================

def generate_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, "RAPPORT D'INVESTIGATION NUMERIQUE FORENSIQUE", ln=True, align='C')
    pdf.ln(5)

    report_text = (
        report_text
        .replace('œ', 'oe').replace('Œ', 'OE')
        .replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
    )

    for line in report_text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
        if line.startswith('#'):
            clean_title = line.replace('#', '').replace('*', '').strip().upper()
            pdf.set_font("Arial", 'B', 12)
            safe_title = clean_title.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, txt=safe_title)
            pdf.ln(2)
        else:
            clean_line = line.replace('**', '').replace('*', '-').replace('`', '')
            pdf.set_font("Arial", size=11)
            safe_line = clean_line.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 6, txt=safe_line)

    return pdf.output(dest="S").encode("latin-1")


# =============================================================================
# PARSING PCAP AVEC SCAPY
# =============================================================================

def parse_pcap(pcap_path):
    """
    Parse le fichier .pcap avec Scapy.
    Retourne un dictionnaire avec toutes les données extraites.
    """
    try:
        from scapy.all import rdpcap, TCP, IP, Raw
    except ImportError:
        st.error("❌ Scapy n'est pas installé. Exécutez : pip install scapy")
        return None

    paquets = rdpcap(pcap_path)

    total_paquets       = len(paquets)
    ips_src             = defaultdict(int)
    ips_dst             = defaultdict(int)
    protocoles          = defaultdict(int)
    sessions_ftp        = []       # Liste de dicts par session
    connexions_timeline = []       # Liste de dicts pour la timeline

    # ── Variables de suivi de session FTP ───────────────────────────────────
    session_courante = {}          # ip_src → données de session en cours
    # ────────────────────────────────────────────────────────────────────────

    for pkt in paquets:
        if not pkt.haslayer(IP):
            continue

        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst
        ips_src[ip_src] += 1
        ips_dst[ip_dst] += 1

        # Protocole de couche transport
        if pkt.haslayer(TCP):
            protocoles['TCP'] += 1
        else:
            protocoles['Autre'] += 1

        # Timestamp du paquet
        ts = float(pkt.time)
        heure = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        date  = datetime.fromtimestamp(ts).strftime('%d/%m/%Y')

        # ── Détection FTP (port 21 TCP) ──────────────────────────────────
        if pkt.haslayer(TCP) and pkt.haslayer(Raw):
            port_src = pkt[TCP].sport
            port_dst = pkt[TCP].dport

            if port_dst == 21 or port_src == 21:
                try:
                    payload = pkt[Raw].load.decode('utf-8', errors='ignore').strip()
                except Exception:
                    payload = ""

                if not payload:
                    continue

                protocoles['FTP'] = protocoles.get('FTP', 0) + 1

                # Clé de session : paire IP
                cle = f"{ip_src}→{ip_dst}" if port_dst == 21 else f"{ip_dst}→{ip_src}"

                if cle not in session_courante:
                    session_courante[cle] = {
                        'ip_client'  : ip_src if port_dst == 21 else ip_dst,
                        'ip_serveur' : ip_dst if port_dst == 21 else ip_src,
                        'utilisateur': None,
                        'mot_de_passe': None,
                        'commandes'  : [],
                        'fichiers_recus'  : [],
                        'fichiers_envoyes': [],
                        'dossiers_visites': [],
                        'debut'      : heure,
                        'date'       : date,
                        'score'      : 0,
                    }

                sess = session_courante[cle]

                # Analyse des commandes FTP
                payload_upper = payload.upper()

                if payload_upper.startswith('USER '):
                    nom = payload[5:].strip()
                    sess['utilisateur'] = nom
                    sess['commandes'].append(f"USER {nom}")
                    sess['score'] += 1

                elif payload_upper.startswith('PASS '):
                    mdp = payload[5:].strip()
                    sess['mot_de_passe'] = mdp
                    sess['commandes'].append(f"PASS {mdp}")
                    sess['score'] += 3   # Credentials en clair = critique

                elif payload_upper.startswith('RETR '):
                    fichier = payload[5:].strip()
                    sess['fichiers_recus'].append(fichier)
                    sess['commandes'].append(f"RETR {fichier}")
                    sess['score'] += 5   # Téléchargement = très suspect

                elif payload_upper.startswith('STOR '):
                    fichier = payload[5:].strip()
                    sess['fichiers_envoyes'].append(fichier)
                    sess['commandes'].append(f"STOR {fichier}")
                    sess['score'] += 5

                elif payload_upper.startswith('CWD ') or payload_upper.startswith('CD '):
                    dossier = payload[4:].strip()
                    sess['dossiers_visites'].append(dossier)
                    sess['commandes'].append(f"CWD {dossier}")
                    sess['score'] += 1

                elif payload_upper.startswith('DELE '):
                    fichier = payload[5:].strip()
                    sess['commandes'].append(f"DELE {fichier}")
                    sess['score'] += 4   # Suppression = suspect

                elif payload_upper.startswith('MKD ') or payload_upper.startswith('RMD '):
                    sess['commandes'].append(payload.strip())
                    sess['score'] += 2

                elif any(payload_upper.startswith(cmd) for cmd in ('QUIT', 'BYE')):
                    # Fin de session → on la sauvegarde
                    sess['commandes'].append('QUIT')
                    sess['fin'] = heure
                    sessions_ftp.append(dict(sess))
                    del session_courante[cle]

                # Timeline
                connexions_timeline.append({
                    'Date'    : date,
                    'Heure'   : heure,
                    'Source'  : ip_src,
                    'Dest'    : ip_dst,
                    'Protocole': 'FTP',
                    'Commande': payload[:60],
                })

    # Sauvegarder les sessions qui ne se sont pas terminées proprement (pas de QUIT)
    for cle, sess in session_courante.items():
        if sess['commandes']:
            sess.setdefault('fin', 'N/A')
            sessions_ftp.append(dict(sess))

    # Niveau de risque par session
    for sess in sessions_ftp:
        s = sess['score']
        if s >= 10:
            sess['niveau'] = 'CRITIQUE'
            sess['couleur'] = '🔴'
        elif s >= 6:
            sess['niveau'] = 'ÉLEVÉ'
            sess['couleur'] = '🟠'
        elif s >= 3:
            sess['niveau'] = 'MOYEN'
            sess['couleur'] = '🟡'
        else:
            sess['niveau'] = 'FAIBLE'
            sess['couleur'] = '🟢'

    return {
        'total_paquets'      : total_paquets,
        'ips_src'            : dict(ips_src),
        'ips_dst'            : dict(ips_dst),
        'protocoles'         : dict(protocoles),
        'sessions_ftp'       : sessions_ftp,
        'timeline'           : connexions_timeline,
    }


# =============================================================================
# GÉNÉRATION RAPPORT IA (GEMINI)
# =============================================================================

def generer_rapport_pcap_ia(resultats, api_key):
    """Génère un rapport d'investigation PCAP via Gemini 2.5 Flash."""

    sessions  = resultats['sessions_ftp']
    total_pkt = resultats['total_paquets']

    nb_sessions   = len(sessions)
    nb_critiques  = len([s for s in sessions if s['niveau'] == 'CRITIQUE'])
    nb_fichiers   = sum(len(s['fichiers_recus']) + len(s['fichiers_envoyes']) for s in sessions)
    credentials   = [f"{s['utilisateur']}:{s['mot_de_passe']}" for s in sessions if s['utilisateur']]

    top_sessions = sorted(sessions, key=lambda x: x['score'], reverse=True)[:5]
    payload_sessions = [
        {
            'ip_client'       : s['ip_client'],
            'ip_serveur'      : s['ip_serveur'],
            'utilisateur'     : s['utilisateur'],
            'fichiers_recus'  : s['fichiers_recus'],
            'fichiers_envoyes': s['fichiers_envoyes'],
            'dossiers'        : s['dossiers_visites'],
            'score'           : s['score'],
            'niveau'          : s['niveau'],
        }
        for s in top_sessions
    ]

    prompt = f"""Agissez en tant qu'Expert Analyste DFIR (Digital Forensics and Incident Response).
Rédigez un rapport d'investigation formel, structuré et impartial pour le dossier #2026-TC.
Périmètre technique : Analyse du trafic réseau (PCAP) — Protocole FTP.
Analyste désigné : Ismail.

DONNÉES EXTRAITES DE LA CAPTURE RÉSEAU :
- Total paquets analysés : {total_pkt}
- Sessions FTP détectées : {nb_sessions}
- Sessions de niveau CRITIQUE : {nb_critiques}
- Fichiers transférés (RETR/STOR) : {nb_fichiers}
- Identifiants FTP en clair détectés : {credentials}
- Détail des sessions les plus suspectes : {payload_sessions}

INSTRUCTIONS DE RÉDACTION :
1. TON : Académique, objectif, factuel et procédural.
2. EN-TÊTE OBLIGATOIRE :
🏛️ DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES (DFIR) 🏛️
**RAPPORT D'EXPERTISE FORENSIQUE : PÔLE RÉSEAU & PCAP**
**Date d'émission :** {datetime.now().strftime('%d %B %Y')}
**Référence Dossier :** #2026-TC
**Analyste Réseau :** Ismail

3. STRUCTURE EXIGÉE :
# I. RÉSUMÉ EXÉCUTIF
# II. ANALYSE DU PROTOCOLE FTP (VULNÉRABILITÉS ET RISQUES)
# III. SESSIONS SUSPECTES ET TRANSFERTS IDENTIFIÉS
# IV. INDICATEURS DE COMPROMISSION (IoC)
# V. CONCLUSION TECHNIQUE ET RECOMMANDATIONS

4. FORMATAGE : Markdown standard. Pas de blocs de code (```). Pas d'indentation en début de ligne.
"""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    full_report  = ""
    report_ph    = st.empty()
    response     = model.generate_content(prompt, stream=True)

    for chunk in response:
        try:
            full_report += chunk.text
            report_ph.markdown(full_report + " ▌")
        except Exception:
            continue

    return full_report


# =============================================================================
# FONCTION PRINCIPALE run()
# =============================================================================

def run():
    load_dotenv()

    locked_msg = (
        "🔒 **Section verrouillée.** En attente d'ingestion du fichier PCAP. "
        "Veuillez uploader `reseau.pcap` dans l'onglet **0. UPLOAD** pour débloquer l'analyse."
    )

    # ── Initialisation session_state ─────────────────────────────────────────
    if 'pcap_resultats' not in st.session_state:
        st.session_state.pcap_resultats = None
    if 'pcap_rapport_ia' not in st.session_state:
        st.session_state.pcap_rapport_ia = None

    # ── En-tête ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <h1 style="margin:0; color:#1E3A8A;">📡 Pôle d'Analyse : Trafic Réseau (PCAP)</h1>
    </div>
    <p style="font-size:14px; color:gray;">
        <b>Analyste Principal :</b> Ismail &nbsp;|&nbsp;
        <b>Cible :</b> reseau.pcap &nbsp;|&nbsp;
        <b>Outils :</b> Scapy, Python Data-Stack, Gemini 2.5 Flash
    </p>
    <hr style="margin-top:0px; margin-bottom:20px;">
    """, unsafe_allow_html=True)

    # ── CSS Upload zone ───────────────────────────────────────────────────────
    st.markdown("""
    <style>
        [data-testid="stFileUploader"] {
            background-color: #f0fdf4;
            border: 2px dashed #16a34a;
            border-radius: 15px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        [data-testid="stFileUploader"]:hover {
            background-color: #dcfce7;
            border-color: #dc2626;
        }
        [data-testid="stFileUploader"] button {
            background-color: #16a34a;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_upload, tab_synth, tab_ftp, tab_conn, tab_conclusion, tab_ia = st.tabs([
        "📥 0. UPLOAD",
        "📊 1. SYNTHÈSE",
        "📂 2. SESSIONS FTP",
        "🌐 3. CONNEXIONS",
        "⚖️ 4. CONCLUSION",
        "🤖 5. RAPPORT IA",
    ])

    # =========================================================================
    # TAB 0 : UPLOAD
    # =========================================================================
    with tab_upload:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    padding: 30px; border-radius: 15px; text-align: center;
                    border: 1px solid #86efac; margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #15803d; margin-top: 0px; font-weight: 800;">
                ☁️ Espace de Téléversement Sécurisé
            </h2>
            <p style="color: #14532d; font-size: 16px; margin-bottom: 0px;">
                Glissez et déposez votre capture réseau <b>.pcap</b> ici.
            </p>
        </div>
        """, unsafe_allow_html=True)

        pcap_file = st.file_uploader(
            "Uploadez votre fichier ici",
            accept_multiple_files=False,
            type=['pcap', 'pcapng', 'cap'],
            label_visibility="collapsed",
            key="pcap_uploader"
        )

        if pcap_file:
            st.success(f"📦 **Fichier détecté :** `{pcap_file.name}` ({pcap_file.size / 1024:.1f} Ko)")

            # Hash d'intégrité
            md5  = hashlib.md5(pcap_file.getvalue()).hexdigest()
            sha1 = hashlib.sha1(pcap_file.getvalue()).hexdigest()

            c1, c2 = st.columns(2)
            c1.code(f"MD5  : {md5}")
            c2.code(f"SHA1 : {sha1}")

            if st.button("🚀 Lancer l'Analyse Forensique du PCAP",
                         use_container_width=True, type="primary"):

                with st.spinner("🔄 Parsing du PCAP en cours... Extraction des artefacts réseau..."):
                    # Sauvegarde temporaire sur disque (Scapy a besoin d'un path)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp:
                        tmp.write(pcap_file.getvalue())
                        tmp_path = tmp.name

                    try:
                        resultats = parse_pcap(tmp_path)
                        if resultats:
                            st.session_state.pcap_resultats = resultats
                            st.success("✅ Analyse terminée ! Naviguez vers l'onglet **SYNTHÈSE**.")

                            # Récapitulatif
                            col1, col2, col3 = st.columns(3)
                            col1.metric("📦 Paquets analysés",
                                        f"{resultats['total_paquets']:,}")
                            col2.metric("📂 Sessions FTP",
                                        len(resultats['sessions_ftp']))
                            col3.metric("🔴 Sessions CRITIQUES",
                                        len([s for s in resultats['sessions_ftp']
                                             if s['niveau'] == 'CRITIQUE']))
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

    # =========================================================================
    # TAB 1 : SYNTHÈSE
    # =========================================================================
    with tab_synth:
        res = st.session_state.pcap_resultats
        if not res:
            st.warning(locked_msg)
        else:
            sessions = res['sessions_ftp']

            nb_critiques = len([s for s in sessions if s['niveau'] == 'CRITIQUE'])
            nb_fichiers  = sum(len(s['fichiers_recus']) + len(s['fichiers_envoyes'])
                               for s in sessions)
            nb_creds     = len([s for s in sessions if s['utilisateur']])

            # Alerte globale
            if nb_critiques > 0:
                st.error(
                    f"🚨 **ALERTE CRITIQUE : EXFILTRATION FTP DÉTECTÉE** — "
                    f"{nb_critiques} session(s) critique(s) identifiée(s) dans la capture réseau."
                )

            st.markdown("### 📊 Métriques de l'Investigation (Temps Réel)")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Total Paquets",     f"{res['total_paquets']:,}", "Analysés")
            col2.metric("📂 Sessions FTP",       len(sessions),              "Détectées")
            col3.metric("📁 Fichiers Transférés", nb_fichiers,               "RETR / STOR")
            col4.metric("🔑 Credentials",         nb_creds,                  "En clair (FTP)")

            st.markdown("---")

            # Répartition des protocoles
            st.markdown("### 📈 Répartition des Protocoles")
            df_proto = pd.DataFrame(
                list(res['protocoles'].items()),
                columns=['Protocole', 'Paquets']
            )
            st.bar_chart(df_proto.set_index('Protocole'))

            st.markdown("---")

            # Répartition des niveaux de risque FTP
            st.markdown("### 🎯 Niveaux de Risque des Sessions FTP")
            niveaux = {'CRITIQUE': 0, 'ÉLEVÉ': 0, 'MOYEN': 0, 'FAIBLE': 0}
            for s in sessions:
                niveaux[s['niveau']] = niveaux.get(s['niveau'], 0) + 1

            df_niv = pd.DataFrame(
                list(niveaux.items()),
                columns=['Niveau', 'Sessions']
            )
            st.bar_chart(df_niv.set_index('Niveau'))

            # Top IPs sources
            st.markdown("### 🌐 Top IPs Sources")
            top_ips = sorted(res['ips_src'].items(), key=lambda x: x[1], reverse=True)[:10]
            df_ips  = pd.DataFrame(top_ips, columns=['IP Source', 'Paquets envoyés'])
            st.dataframe(df_ips, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 2 : SESSIONS FTP
    # =========================================================================
    with tab_ftp:
        res = st.session_state.pcap_resultats
        if not res:
            st.warning(locked_msg)
        else:
            sessions = res['sessions_ftp']

            st.markdown("""
            <style>
                .ftp-card  { background:#f8fafc; border-left:4px solid #0284c7;
                             padding:15px; border-radius:5px; margin-bottom:15px;
                             border:1px solid #e2e8f0; }
                .ftp-crit  { background:#fef2f2; border-left:4px solid #dc2626;
                             padding:15px; border-radius:5px; margin-bottom:15px; }
                .ftp-mono  { font-family:'Courier New',monospace;
                             background:#1e293b; color:#e2e8f0;
                             padding:3px 8px; border-radius:4px; font-size:0.85em; }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 📂 Analyse Forensique des Sessions FTP")
            st.markdown("""
            <div class="ftp-card">
                <h4 style="margin-top:0; color:#0f172a;">ℹ️ Contexte Médico-Légal</h4>
                Le protocole FTP (port 21) transmet les identifiants et les données <b>en clair</b>,
                sans chiffrement. Toute session FTP est donc un vecteur d'exfiltration
                et une source d'artefacts réseau directement exploitables en forensique.
                <br><br>
                <b>Artefact ciblé :</b>
                <span class="ftp-mono">reseau.pcap</span> — Flux TCP port 21
            </div>
            """, unsafe_allow_html=True)

            if not sessions:
                st.info("ℹ️ Aucune session FTP détectée dans ce fichier PCAP.")
            else:
                # Filtres
                filtre_niv = st.selectbox(
                    "🔍 Filtrer par niveau de risque",
                    ['Tous', 'CRITIQUE', 'ÉLEVÉ', 'MOYEN', 'FAIBLE'],
                    key='filtre_ftp'
                )
                sessions_filtrees = (
                    sessions if filtre_niv == 'Tous'
                    else [s for s in sessions if s['niveau'] == filtre_niv]
                )

                st.markdown(f"**{len(sessions_filtrees)} session(s) affichée(s)**")

                for i, sess in enumerate(sessions_filtrees, 1):
                    couleur_border = {
                        'CRITIQUE': '#dc2626', 'ÉLEVÉ': '#ea580c',
                        'MOYEN'   : '#ca8a04', 'FAIBLE': '#16a34a'
                    }.get(sess['niveau'], '#64748b')

                    with st.expander(
                        f"{sess['couleur']} Session #{i} | "
                        f"{sess['ip_client']} → {sess['ip_serveur']} | "
                        f"Niveau : {sess['niveau']} | Score : {sess['score']}"
                    ):
                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.markdown("**🖥️ Informations de Session**")
                            st.markdown(f"- **IP Client :** `{sess['ip_client']}`")
                            st.markdown(f"- **IP Serveur :** `{sess['ip_serveur']}`")
                            st.markdown(f"- **Date :** {sess.get('date', 'N/A')}")
                            st.markdown(f"- **Début :** {sess.get('debut', 'N/A')} "
                                        f"| **Fin :** {sess.get('fin', 'N/A')}")

                        with col_b:
                            st.markdown("**🔑 Credentials (En Clair)**")
                            if sess['utilisateur']:
                                st.error(
                                    f"👤 USER : `{sess['utilisateur']}`\n\n"
                                    f"🔓 PASS : `{sess['mot_de_passe'] or 'Non capturé'}`"
                                )
                            else:
                                st.info("Identifiants non capturés dans cette session.")

                        st.markdown("**📁 Fichiers Transférés**")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("*Reçus (RETR) :*")
                            if sess['fichiers_recus']:
                                for f in sess['fichiers_recus']:
                                    st.markdown(f"  - `{f}`")
                            else:
                                st.caption("Aucun")
                        with c2:
                            st.markdown("*Envoyés (STOR) :*")
                            if sess['fichiers_envoyes']:
                                for f in sess['fichiers_envoyes']:
                                    st.markdown(f"  - `{f}`")
                            else:
                                st.caption("Aucun")

                        if sess['dossiers_visites']:
                            st.markdown("**📂 Dossiers Explorés (CWD)**")
                            for d in sess['dossiers_visites']:
                                st.markdown(f"  - `{d}`")

                        st.markdown("**📋 Journal des Commandes FTP**")
                        st.code('\n'.join(sess['commandes']), language='bash')

                        # Interprétation dynamique
                        if sess['niveau'] in ('CRITIQUE', 'ÉLEVÉ'):
                            nb_f = (len(sess['fichiers_recus'])
                                    + len(sess['fichiers_envoyes']))
                            st.markdown(
                                f"""
                                <div style="background:#fef2f2; border-left:4px solid #dc2626;
                                            padding:12px; border-radius:5px; margin-top:10px;
                                            border:1px solid #fecaca;">
                                    <b>⚖️ Interprétation Forensique</b><br>
                                    La session FTP entre <b>{sess['ip_client']}</b> et
                                    <b>{sess['ip_serveur']}</b> présente un score de risque de
                                    <b>{sess['score']}</b>. Les credentials ont été transmis
                                    en clair et <b>{nb_f} fichier(s)</b> ont été transférés.
                                    Ce comportement constitue un indicateur fort d'exfiltration.
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

    # =========================================================================
    # TAB 3 : CONNEXIONS & TIMELINE
    # =========================================================================
    with tab_conn:
        res = st.session_state.pcap_resultats
        if not res:
            st.warning(locked_msg)
        else:
            st.markdown("### 🌐 Carte des Connexions Réseau")

            timeline = res['timeline']

            if not timeline:
                st.info("ℹ️ Aucun échange FTP à afficher dans la timeline.")
            else:
                # Timeline complète
                df_tl = pd.DataFrame(timeline)
                st.markdown("#### ⏱️ Timeline des Échanges FTP")
                st.dataframe(df_tl, use_container_width=True, hide_index=True)

                # Top IPs destinations
                st.markdown("#### 🎯 Top IPs Destinations")
                top_dst = sorted(
                    res['ips_dst'].items(), key=lambda x: x[1], reverse=True
                )[:10]
                df_dst = pd.DataFrame(top_dst, columns=['IP Destination', 'Paquets reçus'])
                st.dataframe(df_dst, use_container_width=True, hide_index=True)

                # Paires src → dst les plus actives
                st.markdown("#### 🔗 Paires de Communication les Plus Actives")
                paires = defaultdict(int)
                for row in timeline:
                    paires[f"{row['Source']} → {row['Dest']}"] += 1
                top_paires = sorted(paires.items(), key=lambda x: x[1], reverse=True)[:10]
                df_paires  = pd.DataFrame(top_paires, columns=['Paire', 'Échanges'])
                st.bar_chart(df_paires.set_index('Paire'))

    # =========================================================================
    # TAB 4 : CONCLUSION
    # =========================================================================
    with tab_conclusion:
        res = st.session_state.pcap_resultats
        if not res:
            st.warning(locked_msg)
        else:
            sessions = res['sessions_ftp']

            nb_crit     = len([s for s in sessions if s['niveau'] == 'CRITIQUE'])
            nb_fichiers = sum(len(s['fichiers_recus']) + len(s['fichiers_envoyes'])
                              for s in sessions)
            has_creds   = any(s['utilisateur'] for s in sessions)
            top_s       = sorted(sessions, key=lambda x: x['score'], reverse=True)

            # Verdict
            if nb_crit >= 1 and has_creds:
                verdict_css   = "#991b1b"
                verdict_bg    = "#fef2f2"
                verdict_label = "⚠️ EXFILTRATION FTP AVÉRÉE"
                verdict_detail = (
                    f"La capture réseau révèle <b>{nb_crit} session(s) critique(s)</b>, "
                    f"avec transmission de credentials en clair et "
                    f"<b>{nb_fichiers} transfert(s)</b> de fichiers documentés."
                )
            elif nb_fichiers > 0:
                verdict_css    = "#92400e"
                verdict_bg     = "#fffbeb"
                verdict_label  = "⚠️ ACTIVITÉ FTP SUSPECTE"
                verdict_detail = (
                    f"{nb_fichiers} transfert(s) de fichiers détecté(s). "
                    f"Corrélation avec les autres artefacts requise."
                )
            else:
                verdict_css    = "#1e3a8a"
                verdict_bg     = "#eff6ff"
                verdict_label  = "ℹ️ AUCUNE ACTIVITÉ SUSPECTE MAJEURE"
                verdict_detail = "Aucune session FTP critique détectée dans cette capture."

            st.markdown(
                f"""
                <div style="background:{verdict_bg}; border-left:8px solid {verdict_css};
                            padding:25px; border-radius:8px; margin-bottom:25px;
                            box-shadow:0 4px 10px rgba(0,0,0,0.08);">
                    <h3 style="color:{verdict_css}; margin-top:0;">{verdict_label}</h3>
                    <p style="color:{verdict_css}; margin-bottom:0; line-height:1.6;">
                        {verdict_detail}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Chaîne de garde
            st.markdown("### 🔐 Chaîne de Garde (Chain of Custody)")
            md5_pcap  = "Non calculé"
            sha1_pcap = "Non calculé"

            coc_text = f"""
╔══════════════════════════════════════════════════════════╗
║       CHAIN OF CUSTODY — TECHCORP #2026-TC               ║
╠══════════════════════════════════════════════════════════╣
  Affaire        : TechCorp — Exfiltration Projet Orion
  Pièce          : reseau.pcap
  Analyste       : Ismail
  Date analyse   : {datetime.now().strftime('%d/%m/%Y %H:%M')}
  Outil          : Scapy — Python 3.x
  Standard       : ISO/IEC 27037:2012
╠══════════════════════════════════════════════════════════╣
  RÉSULTATS :
  Paquets analysés     : {res['total_paquets']:,}
  Sessions FTP         : {len(sessions)}
  Sessions CRITIQUES   : {nb_crit}
  Fichiers transférés  : {nb_fichiers}
  Credentials en clair : {"OUI" if has_creds else "NON"}
╚══════════════════════════════════════════════════════════╝
"""
            st.code(coc_text, language='text')

            st.download_button(
                label="📥 Télécharger la Chain of Custody (.txt)",
                data=coc_text,
                file_name="chain_of_custody_pcap_2026TC.txt",
                mime="text/plain"
            )

            # Résumé des sessions suspectes
            if top_s:
                st.markdown("### 🚨 Top Sessions Suspectes")
                df_top = pd.DataFrame([{
                    'IP Client'    : s['ip_client'],
                    'IP Serveur'   : s['ip_serveur'],
                    'Utilisateur'  : s['utilisateur'] or 'N/A',
                    'Fichiers'     : len(s['fichiers_recus']) + len(s['fichiers_envoyes']),
                    'Score'        : s['score'],
                    'Niveau'       : f"{s['couleur']} {s['niveau']}",
                } for s in top_s[:5]])
                st.dataframe(df_top, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 5 : RAPPORT IA
    # =========================================================================
    with tab_ia:
        res = st.session_state.pcap_resultats
        if not res:
            st.warning(locked_msg)
        else:
            st.markdown("### 🤖 Génération du Rapport d'Expertise PCAP")
            st.info(
                "Ce module exploite Gemini 2.5 Flash pour rédiger un rapport d'investigation "
                "formel, basé exclusivement sur les artefacts réseau extraits du fichier PCAP."
            )

            # Clé API
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                st.success("🔒 Clé API chargée de manière sécurisée via l'environnement local.")
            else:
                st.warning("⚠️ Clé API introuvable. Veuillez l'insérer manuellement :")
                api_key = st.text_input("🔑 Clé API Google Gemini :", type="password",
                                        key="pcap_api_key")

            if st.button("⚖️ Générer le Rapport Officiel PCAP", type="primary"):
                if not api_key:
                    st.error("❌ Clé API requise pour initialiser le modèle de langage.")
                else:
                    status_box = st.info(
                        "🔄 Initialisation du moteur d'analyse... Transmission des artefacts..."
                    )
                    start_time = time.time()

                    try:
                        rapport = generer_rapport_pcap_ia(res, api_key)
                        elapsed = round(time.time() - start_time, 2)

                        if not rapport.strip():
                            status_box.empty()
                            st.error(
                                "❌ Échec de la génération. "
                                "Le filtre de sécurité de l'API a intercepté la requête."
                            )
                        else:
                            clean_rapport = (
                                rapport
                                .replace("```text", "").replace("```markdown", "")
                                .replace("```", "").strip()
                            )
                            st.session_state.pcap_rapport_ia = clean_rapport
                            status_box.empty()
                            st.success(f"✅ Rapport finalisé en {elapsed} secondes.")

                    except Exception as e:
                        status_box.empty()
                        st.error(f"❌ Anomalie lors de l'appel API : {str(e)}")

            # Affichage et export PDF
            if st.session_state.pcap_rapport_ia:
                rapport_clean = st.session_state.pcap_rapport_ia

                st.markdown(
                    f"""
                    <div style="background:#ffffff; padding:50px; border-radius:4px;
                                box-shadow:0 10px 30px rgba(0,0,0,0.10); margin-top:20px;
                                border-top:15px solid #1e3a8a;
                                font-family:'Times New Roman',serif;
                                color:#111827; line-height:1.6;">
                        {rapport_clean}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                pdf_bytes = generate_pdf_report(rapport_clean)
                st.download_button(
                    label="📥 Exporter le Rapport Officiel (Format PDF)",
                    data=pdf_bytes,
                    file_name="Rapport_Expertise_PCAP_2026_TC.pdf",
                    mime="application/pdf",
                    type="primary"
                )


# =============================================================================
if __name__ == "__main__":
    run()
