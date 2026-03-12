import streamlit as st
import pandas as pd

def run():

    st.title("🌐 Analyse du Trafic Réseau (PCAP)")
    st.markdown("**Examinateur :** Boutoucha Ismail | **Outil :** Wireshark")
    st.markdown("---")

    # ─── Bannière d'alerte principale ───
    st.error("""
🚨 **EXFILTRATION DE DONNÉES CONFIRMÉE** — Le 21 février 2026, Jean Martin (192.168.10.42)
a exfiltré le fichier `projet_orion.tar.gz` (4.2 Mo) via FTP vers un serveur externe,
suivi d'un DNS tunneling et d'une tentative d'espionnage industriel vers un concurrent direct.
""")

    # ════════════════════════════════════════════
    # SECTION 1 — STATISTIQUES GLOBALES
    # ════════════════════════════════════════════
    st.subheader("📊 Statistiques globales de la capture")
    st.caption("Fichier analysé : reseau.pcap | Cas TechCorp — Pièce A")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total paquets",     "5 847")
    col2.metric("🌐 IPs uniques",       "12")
    col3.metric("⏱️ Durée capture",     "5 heures")
    col4.metric("💾 Taille fichier",    "2.8 Mo")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("📅 Début",  "21/02/2026 14:00")
    col6.metric("📅 Fin",    "21/02/2026 19:00")
    col7.metric("⚠️ Paquets suspects", "22")
    col8.metric("🔴 IOCs identifiés",  "5")

    # ─── Répartition des protocoles ───
    st.markdown("#### Répartition des protocoles")
    protocoles_data = pd.DataFrame({
        "Protocole": ["DNS (UDP/53)", "Autres TCP", "TCP", "ARP", "HTTPS (TCP/443)",
                      "SSH (TCP/22)", "NTP (UDP/123)", "FTP-Data (TCP/49932)",
                      "HTTP (TCP/80)", "ICMP", "FTP (TCP/21)", "mDNS (UDP/5353)"],
        "Paquets":   [1720, 2805, 3420, 400, 124, 263, 150, 112, 85, 120, 48, 20],
        "Pourcentage (%)": [29.4, 48.0, 58.5, 6.8, 2.1, 4.5, 2.6, 1.9, 1.5, 2.1, 0.8, 0.3],
    })
    st.dataframe(protocoles_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 2 — CONFIGURATION RÉSEAU
    # ════════════════════════════════════════════
    st.subheader("🖥️ Hôtes identifiés sur le réseau")

    hosts_data = pd.DataFrame([
        {"IP": "192.168.10.42",  "Nom":          "PC Jean Martin",            "MAC": "00:1a:2b:3c:4d:5e", "Rôle": "⚠️ Poste utilisateur suspect"},
        {"IP": "192.168.10.15",  "Nom":          "srv-intern01",               "MAC": "00:1a:2b:3c:4d:10", "Rôle": "🔴 Serveur interne compromis (pivot)"},
        {"IP": "192.168.10.1",   "Nom":          "Gateway/DNS",                "MAC": "00:1a:2b:3c:4d:01", "Rôle": "Passerelle réseau / DNS"},
        {"IP": "192.168.10.20",  "Nom":          "Fileserver",                 "MAC": "00:1a:2b:3c:4d:20", "Rôle": "Serveur de fichiers"},
        {"IP": "192.168.10.5",   "Nom":          "Poste Admin",                "MAC": "00:1a:2b:3c:4d:05", "Rôle": "Poste administrateur"},
        {"IP": "203.0.113.50",   "Nom":          "ftp.securedrop-ext.com",     "MAC": "N/A",               "Rôle": "🔴 Serveur FTP externe (exfiltration)"},
        {"IP": "198.51.100.25",  "Nom":          "novatech-industries.com",    "MAC": "N/A",               "Rôle": "🔴 Site concurrent (espionnage)"},
        {"IP": "142.250.74.100", "Nom":          "www.google.com",             "MAC": "N/A",               "Rôle": "Moteur de recherche"},
        {"IP": "104.26.10.50",   "Nom":          "vpn-provider.net",           "MAC": "N/A",               "Rôle": "⚠️ Fournisseur VPN (connexion bloquée)"},
    ])
    st.dataframe(hosts_data, use_container_width=True, hide_index=True)


    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 3 — TIMELINE DES ÉVÉNEMENTS
    # ════════════════════════════════════════════
    st.subheader("⏱️ Timeline complète des événements suspects")

    timeline_data = pd.DataFrame([
        {"Heure": "14:00:00", "Catégorie": "ℹ️ Capture",         "Événement": "Début de la capture réseau",                     "Gravité": "Info",   "Détails": "Trafic de fond normal (ARP, ICMP, DNS, NTP)"},
        {"Heure": "14:25:03", "Catégorie": "🔍 Reconnaissance",   "Événement": "DNS — srv-intern01.techcorp.local",               "Gravité": "Moyenne","Détails": "Jean Martin résout le nom du serveur interne (192.168.10.15)"},
        {"Heure": "14:30:12", "Catégorie": "🔓 Accès initial",    "Événement": "Session SSH #1 vers srv-intern01",                "Gravité": "Haute",  "Détails": "Port 52847 → 22 | Durée : 22 min | Volume : ~150 Ko chiffrés"},
        {"Heure": "14:35:28", "Catégorie": "⚠️ Résolution C2",   "Événement": "DNS — ftp.securedrop-ext.com",                   "Gravité": "Haute",  "Détails": "srv-intern01 résout le domaine d'exfiltration → 203.0.113.50"},
        {"Heure": "14:36:02", "Catégorie": "📤 Exfiltration",     "Événement": "FTP — Authentification en clair",                "Gravité": "Haute",  "Détails": "USER: jm_drop | PASS: OrionExfil2026! — transmis sans chiffrement"},
        {"Heure": "14:38:05", "Catégorie": "📤 Exfiltration",     "Événement": "Transfert FTP — projet_orion.tar.gz (4.2 Mo)",   "Gravité": "Haute",  "Détails": "Mode PASV | Port 55012 → 49932 | Header gzip détecté (1f 8b 08 00)"},
        {"Heure": "14:47:58", "Catégorie": "📤 Exfiltration",     "Événement": "Transfert FTP terminé",                          "Gravité": "Haute",  "Détails": "226 Transfer complete — 4 398 041 octets exfiltrés avec succès"},
        {"Heure": "14:52:45", "Catégorie": "🔒 Session",          "Événement": "Fin Session SSH #1",                             "Gravité": "Haute",  "Détails": "TCP FIN/ACK | 22 min 33 sec de session"},
        {"Heure": "17:58:12", "Catégorie": "🌐 Navigation",       "Événement": "DNS + HTTPS — www.google.com",                   "Gravité": "Basse",  "Détails": "Recherches Google (contenu chiffré, probablement lié à la fuite)"},
        {"Heure": "18:05:12", "Catégorie": "🚨 DNS Tunneling",    "Événement": "3 requêtes DNS TXT encodées Base64",             "Gravité": "Haute",  "Détails": "Décodage : 'Projet_Orion', 'Budget_2026', 'Plans_Confid'"},
        {"Heure": "18:08:22", "Catégorie": "🛡️ Évasion",         "Événement": "Tentative VPN bloquée — vpn-provider.net",       "Gravité": "Haute",  "Détails": "SYN TCP/443 → RST/ACK par le firewall"},
        {"Heure": "18:15:03", "Catégorie": "🕵️ Espionnage",      "Événement": "DNS + HTTPS — novatech-industries.com",          "Gravité": "Haute",  "Détails": "Concurrent direct de TechCorp | SNI: novatech-industries.com"},
        {"Heure": "18:20:05", "Catégorie": "🧹 Anti-forensique",  "Événement": "Session SSH #2 — Nettoyage de traces",           "Gravité": "Haute",  "Détails": "Port 53102 → 22 | 8 min 28 sec | ~45 Ko | Suppression probable de logs"},
        {"Heure": "19:00:00", "Catégorie": "ℹ️ Capture",         "Événement": "Fin de la capture réseau",                       "Gravité": "Info",   "Détails": "Aucune activité suspecte après 18:28:33"},
    ])
    st.dataframe(timeline_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 4 — EXFILTRATION FTP
    # ════════════════════════════════════════════
    st.subheader("📤 Exfiltration FTP — Détails")

    col_a, col_b = st.columns(2)
    with col_a:
        st.error("🔑 **Identifiants FTP interceptés en clair**")
        st.code("USER: jm_drop\nPASS: OrionExfil2026!", language="text")
        st.caption("Les initiales 'jm' correspondent à Jean Martin. 'OrionExfil' contient le nom du projet et le mot 'Exfil'.")

    with col_b:
        st.error("💾 **Fichier exfiltré**")
        st.code("Fichier : projet_orion.tar.gz\nTaille  : 4 398 041 octets (4.2 Mo)\nFormat  : gzip (magic bytes: 1f 8b 08 00)\nDest.   : ftp.securedrop-ext.com (203.0.113.50)\nDurée   : 14:38:05 → 14:47:58 (≈ 10 min)", language="text")

    # Dialogue FTP complet
    with st.expander("📋 Voir le dialogue FTP complet intercepté"):
        ftp_dialog = pd.DataFrame([
            {"Direction": "← Serveur", "Commande/Réponse": "220 SecureDrop FTP Server Ready",                       "Heure": "14:36:02.003"},
            {"Direction": "→ Client",  "Commande/Réponse": "USER jm_drop",                                          "Heure": "14:36:02.005"},
            {"Direction": "← Serveur", "Commande/Réponse": "331 Password required for jm_drop",                    "Heure": "14:36:02.007"},
            {"Direction": "→ Client",  "Commande/Réponse": "PASS OrionExfil2026!",                                  "Heure": "14:36:02.009"},
            {"Direction": "← Serveur", "Commande/Réponse": "230 User jm_drop logged in",                           "Heure": "14:36:02.011"},
            {"Direction": "→ Client",  "Commande/Réponse": "CWD /drop",                                             "Heure": "14:36:02.013"},
            {"Direction": "← Serveur", "Commande/Réponse": "250 CWD command successful",                            "Heure": "14:36:02.015"},
            {"Direction": "→ Client",  "Commande/Réponse": "TYPE I",                                                "Heure": "14:36:02.017"},
            {"Direction": "← Serveur", "Commande/Réponse": "200 Type set to I",                                     "Heure": "14:36:02.019"},
            {"Direction": "→ Client",  "Commande/Réponse": "PASV",                                                  "Heure": "14:36:02.021"},
            {"Direction": "← Serveur", "Commande/Réponse": "227 Entering Passive Mode (203,0,113,50,195,12)",       "Heure": "14:36:02.023"},
            {"Direction": "→ Client",  "Commande/Réponse": "STOR projet_orion.tar.gz",                              "Heure": "14:36:02.025"},
            {"Direction": "← Serveur", "Commande/Réponse": "150 Opening BINARY mode data connection",               "Heure": "14:36:02.027"},
            {"Direction": "← Serveur", "Commande/Réponse": "226 Transfer complete (4398041 bytes)",                 "Heure": "14:47:59.000"},
            {"Direction": "→ Client",  "Commande/Réponse": "QUIT",                                                  "Heure": "14:47:59.002"},
            {"Direction": "← Serveur", "Commande/Réponse": "221 Goodbye",                                           "Heure": "14:47:59.004"},
        ])
        st.dataframe(ftp_dialog, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 5 — SESSIONS TCP PERSISTANTES
    # ════════════════════════════════════════════
    st.subheader("🔗 Sessions TCP persistantes (> 5 minutes)")

    sessions_data = pd.DataFrame([
        {"ID": "SSH-1",    "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Port Src": 52847, "Port Dst": 22,    "Protocole": "SSH",      "Début": "14:30:12", "Fin": "14:52:45", "Durée (min)": 22.55, "Volume": "~150 Ko", "Gravité": "🔴 Haute", "Description": "Exécution de scripts sur srv-intern01"},
        {"ID": "FTP-CTRL", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50", "Port Src": 43218, "Port Dst": 21,    "Protocole": "FTP",      "Début": "14:36:02", "Fin": "14:48:15", "Durée (min)": 12.22, "Volume": "~4.5 Ko", "Gravité": "🔴 Haute", "Description": "Canal de contrôle FTP — identifiants en clair"},
        {"ID": "FTP-DATA", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50", "Port Src": 55012, "Port Dst": 49932, "Protocole": "FTP-Data", "Début": "14:38:05", "Fin": "14:47:58", "Durée (min)": 9.88,  "Volume": "4.2 Mo",  "Gravité": "🔴 Haute", "Description": "Transfert projet_orion.tar.gz (mode PASV)"},
        {"ID": "SSH-2",    "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Port Src": 53102, "Port Dst": 22,    "Protocole": "SSH",      "Début": "18:20:05", "Fin": "18:28:33", "Durée (min)": 8.47,  "Volume": "~45 Ko",  "Gravité": "🔴 Haute", "Description": "Nettoyage post-exfiltration (suppression de logs)"},
    ])
    st.dataframe(sessions_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 6 — DNS TUNNELING
    # ════════════════════════════════════════════
    st.subheader("🚨 DNS Tunneling — Exfiltration de métadonnées")

    st.warning("Trois requêtes DNS de type TXT ont été émises vers `*.tun.securedrop-ext.com` avec des sous-domaines encodés en Base64. Cette technique permet d'exfiltrer des données en les dissimulant dans des requêtes DNS apparemment légitimes.")

    dns_tunnel = pd.DataFrame([
        {"Heure": "18:05:12", "Sous-domaine encodé (Base64)": "UHJvamV0X09yaW9u",  "Décodé": "Projet_Orion",  "Type": "TXT", "Réponse": "NXDOMAIN", "Gravité": "🔴 Haute"},
        {"Heure": "18:05:14", "Sous-domaine encodé (Base64)": "QnVkZ2V0XzIwMjY=",  "Décodé": "Budget_2026",   "Type": "TXT", "Réponse": "NXDOMAIN", "Gravité": "🔴 Haute"},
        {"Heure": "18:05:15", "Sous-domaine encodé (Base64)": "UGxhbnNfQ29uZmlk", "Décodé": "Plans_Confid",  "Type": "TXT", "Réponse": "NXDOMAIN", "Gravité": "🔴 Haute"},
    ])
    st.dataframe(dns_tunnel, use_container_width=True, hide_index=True)
    st.caption("Les noms décodés confirment que les données sensibles du projet Orion, les budgets 2026 et des plans confidentiels ont été exfiltrés via DNS.")

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 7 — REQUÊTES DNS SUSPECTES
    # ════════════════════════════════════════════
    st.subheader("🌐 Requêtes DNS suspectes")

    dns_data = pd.DataFrame([
        {"Heure": "14:25:03", "IP Source": "192.168.10.42", "Domaine": "srv-intern01.techcorp.local",           "Type": "A",   "Résolu vers": "192.168.10.15", "Catégorie": "Reconnaissance",       "Gravité": "🟡 Moyenne"},
        {"Heure": "14:35:28", "IP Source": "192.168.10.15", "Domaine": "ftp.securedrop-ext.com",               "Type": "A",   "Résolu vers": "203.0.113.50",  "Catégorie": "Exfiltration C2",      "Gravité": "🔴 Haute"},
        {"Heure": "18:05:12", "IP Source": "192.168.10.42", "Domaine": "UHJvamV0X09yaW9u.tun.securedrop-ext.com","Type": "TXT", "Résolu vers": "NXDOMAIN",      "Catégorie": "DNS Tunneling",        "Gravité": "🔴 Haute"},
        {"Heure": "18:05:14", "IP Source": "192.168.10.42", "Domaine": "QnVkZ2V0XzIwMjY=.tun.securedrop-ext.com","Type": "TXT", "Résolu vers": "NXDOMAIN",      "Catégorie": "DNS Tunneling",        "Gravité": "🔴 Haute"},
        {"Heure": "18:05:15", "IP Source": "192.168.10.42", "Domaine": "UGxhbnNfQ29uZmlk.tun.securedrop-ext.com","Type": "TXT", "Résolu vers": "NXDOMAIN",      "Catégorie": "DNS Tunneling",        "Gravité": "🔴 Haute"},
        {"Heure": "18:08:22", "IP Source": "192.168.10.42", "Domaine": "vpn-provider.net",                     "Type": "A",   "Résolu vers": "104.26.10.50",  "Catégorie": "Évasion / VPN",        "Gravité": "🔴 Haute"},
        {"Heure": "18:15:03", "IP Source": "192.168.10.42", "Domaine": "novatech-industries.com",              "Type": "A",   "Résolu vers": "198.51.100.25", "Catégorie": "Espionnage industriel","Gravité": "🔴 Haute"},
        {"Heure": "17:58:12", "IP Source": "192.168.10.42", "Domaine": "www.google.com",                       "Type": "A",   "Résolu vers": "142.250.74.100","Catégorie": "Navigation",           "Gravité": "🟢 Basse"},
    ])
    st.dataframe(dns_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 8 — IOCs
    # ════════════════════════════════════════════
    st.subheader("🎯 IOC — Indicateurs de Compromission")

    ioc_data = pd.DataFrame([
        {"IP": "192.168.10.42", "Nom hôte": "PC Jean Martin",         "Type de menace": "Insider Threat — Acteur principal",    "Premier vu": "14:25:03", "Dernier vu": "18:28:33", "Gravité": "🔴 Haute", "Preuves": "Sessions SSH, DNS tunneling, navigation NovaTech, tentative VPN"},
        {"IP": "203.0.113.50",  "Nom hôte": "ftp.securedrop-ext.com", "Type de menace": "Serveur d'exfiltration (C2)",          "Premier vu": "14:35:28", "Dernier vu": "14:48:15", "Gravité": "🔴 Haute", "Preuves": "Résolution DNS + transfert FTP de 4.2 Mo (projet_orion.tar.gz)"},
        {"IP": "192.168.10.15", "Nom hôte": "srv-intern01",           "Type de menace": "Serveur compromis (pivot)",            "Premier vu": "14:30:12", "Dernier vu": "18:28:33", "Gravité": "🔴 Haute", "Preuves": "Cible des sessions SSH, utilisé comme relais FTP"},
        {"IP": "198.51.100.25", "Nom hôte": "novatech-industries.com","Type de menace": "Destination suspecte — Concurrent",    "Premier vu": "18:15:03", "Dernier vu": "18:15:45", "Gravité": "🔴 Haute", "Preuves": "Requête DNS + session HTTPS (SNI: novatech-industries.com)"},
        {"IP": "104.26.10.50",  "Nom hôte": "vpn-provider.net",       "Type de menace": "Tentative d'évasion réseau",           "Premier vu": "18:08:22", "Dernier vu": "18:08:55", "Gravité": "🔴 Haute", "Preuves": "DNS resolve + SYN TCP/443 → RST/ACK (firewall block)"},
    ])
    st.dataframe(ioc_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 9 — PAQUETS SUSPECTS
    # ════════════════════════════════════════════
    st.subheader("📦 Tableau des paquets suspects")

    packets_data = pd.DataFrame([
        {"Heure": "14:25:03.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS",      "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 78,   "Raison": "Résolution srv-intern01 — reconnaissance",              "Gravité": "🟡 Moyenne"},
        {"Heure": "14:30:12.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Protocole": "TCP SYN",  "Port Src": 52847,       "Port Dst": 22,    "Taille": 62,   "Raison": "Début session SSH #1",                                  "Gravité": "🔴 Haute"},
        {"Heure": "14:30:12.002", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Protocole": "SSH",      "Port Src": 52847,       "Port Dst": 22,    "Taille": 95,   "Raison": "SSH banner: OpenSSH_for_Windows_8.6",                   "Gravité": "🔴 Haute"},
        {"Heure": "14:35:28.000", "IP Source": "192.168.10.15", "IP Dest": "192.168.10.1",  "Protocole": "DNS",      "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 82,   "Raison": "Résolution ftp.securedrop-ext.com — C2",                "Gravité": "🔴 Haute"},
        {"Heure": "14:36:02.000", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "TCP SYN",  "Port Src": 43218,       "Port Dst": 21,    "Taille": 62,   "Raison": "Connexion FTP vers serveur externe",                    "Gravité": "🔴 Haute"},
        {"Heure": "14:36:02.005", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "FTP",      "Port Src": 43218,       "Port Dst": 21,    "Taille": 76,   "Raison": "USER jm_drop (identifiant en clair)",                   "Gravité": "🔴 Haute"},
        {"Heure": "14:36:02.009", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "FTP",      "Port Src": 43218,       "Port Dst": 21,    "Taille": 82,   "Raison": "PASS OrionExfil2026! (mot de passe en clair)",          "Gravité": "🔴 Haute"},
        {"Heure": "14:36:02.025", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "FTP",      "Port Src": 43218,       "Port Dst": 21,    "Taille": 88,   "Raison": "STOR projet_orion.tar.gz (envoi fichier)",              "Gravité": "🔴 Haute"},
        {"Heure": "14:38:05.000", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "FTP-Data", "Port Src": 55012,       "Port Dst": 49932, "Taille": 1514, "Raison": "Début transfert — header gzip (1f 8b 08 00)",           "Gravité": "🔴 Haute"},
        {"Heure": "14:47:58.000", "IP Source": "192.168.10.15", "IP Dest": "203.0.113.50",  "Protocole": "FTP-Data", "Port Src": 55012,       "Port Dst": 49932, "Taille": 1460, "Raison": "Dernier segment — 4 398 041 octets transférés",         "Gravité": "🔴 Haute"},
        {"Heure": "14:47:59.000", "IP Source": "203.0.113.50",  "IP Dest": "192.168.10.15", "Protocole": "FTP",      "Port Src": 21,          "Port Dst": 43218, "Taille": 96,   "Raison": "226 Transfer complete (4398041 bytes)",                 "Gravité": "🔴 Haute"},
        {"Heure": "14:52:45.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Protocole": "TCP FIN",  "Port Src": 52847,       "Port Dst": 22,    "Taille": 54,   "Raison": "Fin session SSH #1 (22 min 33 sec)",                    "Gravité": "🔴 Haute"},
        {"Heure": "18:05:12.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS TXT",  "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 98,   "Raison": "DNS Tunnel: UHJvamV0X09yaW9u → 'Projet_Orion'",        "Gravité": "🔴 Haute"},
        {"Heure": "18:05:14.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS TXT",  "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 98,   "Raison": "DNS Tunnel: QnVkZ2V0XzIwMjY= → 'Budget_2026'",         "Gravité": "🔴 Haute"},
        {"Heure": "18:05:15.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS TXT",  "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 98,   "Raison": "DNS Tunnel: UGxhbnNfQ29uZmlk → 'Plans_Confid'",        "Gravité": "🔴 Haute"},
        {"Heure": "18:08:22.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS",      "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 76,   "Raison": "Résolution vpn-provider.net — tentative évasion",       "Gravité": "🔴 Haute"},
        {"Heure": "18:08:55.000", "IP Source": "192.168.10.42", "IP Dest": "104.26.10.50",  "Protocole": "TCP SYN",  "Port Src": 54800,       "Port Dst": 443,   "Taille": 62,   "Raison": "SYN vers VPN — connexion bloquée",                     "Gravité": "🔴 Haute"},
        {"Heure": "18:08:55.500", "IP Source": "104.26.10.50",  "IP Dest": "192.168.10.42", "Protocole": "TCP RST",  "Port Src": 443,         "Port Dst": 54800, "Taille": 54,   "Raison": "RST/ACK firewall — VPN bloqué",                        "Gravité": "🔴 Haute"},
        {"Heure": "18:15:03.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.1",  "Protocole": "DNS",      "Port Src": "ephemeral", "Port Dst": 53,    "Taille": 82,   "Raison": "Résolution novatech-industries.com — concurrent",       "Gravité": "🔴 Haute"},
        {"Heure": "18:15:45.000", "IP Source": "192.168.10.42", "IP Dest": "198.51.100.25", "Protocole": "TLS",      "Port Src": 55100,       "Port Dst": 443,   "Taille": 280,  "Raison": "TLS ClientHello SNI: novatech-industries.com",          "Gravité": "🔴 Haute"},
        {"Heure": "18:20:05.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Protocole": "TCP SYN",  "Port Src": 53102,       "Port Dst": 22,    "Taille": 62,   "Raison": "Début session SSH #2 — nettoyage",                     "Gravité": "🔴 Haute"},
        {"Heure": "18:28:33.000", "IP Source": "192.168.10.42", "IP Dest": "192.168.10.15", "Protocole": "TCP FIN",  "Port Src": 53102,       "Port Dst": 22,    "Taille": 54,   "Raison": "Fin session SSH #2 (8 min 28 sec)",                    "Gravité": "🔴 Haute"},
    ])
    st.dataframe(packets_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 10 — FILTRES WIRESHARK
    # ════════════════════════════════════════════
    st.subheader("🔎 Filtres Wireshark recommandés")

    filters_data = pd.DataFrame([
        {"Nom":              "SSH Session #1",    "Filtre Wireshark": 'ip.addr == 192.168.10.42 && tcp.port == 52847'},
        {"Nom":              "SSH Session #2",    "Filtre Wireshark": 'ip.addr == 192.168.10.42 && tcp.port == 53102'},
        {"Nom":              "FTP Contrôle",      "Filtre Wireshark": 'ftp && ip.addr == 203.0.113.50'},
        {"Nom":              "FTP Données",       "Filtre Wireshark": 'ip.addr == 203.0.113.50 && tcp.port == 49932'},
        {"Nom":              "DNS Suspects",      "Filtre Wireshark": 'dns && (dns.qry.name contains "securedrop" || dns.qry.name contains "novatech" || dns.qry.name contains "vpn")'},
        {"Nom":              "DNS Tunneling",     "Filtre Wireshark": 'dns.qry.name contains "tun.securedrop"'},
        {"Nom":              "TLS NovaTech",      "Filtre Wireshark": 'tls.handshake.extensions_server_name contains "novatech"'},
        {"Nom":              "Tout le PC suspect","Filtre Wireshark": 'ip.addr == 192.168.10.42'},
        {"Nom":              "Tout le serveur",   "Filtre Wireshark": 'ip.addr == 192.168.10.15'},
    ])
    st.dataframe(filters_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════
    # SECTION 11 — CONCLUSION NARRATIVE
    # ════════════════════════════════════════════
    st.subheader("📝 Rapport de conclusion forensique")

    st.error("""
**RAPPORT D'ANALYSE FORENSIQUE — PIÈCE À CONVICTION « A » (reseau.pcap)**

Le 21 février 2026, entre 14h00 et 19h00 CET, l'analyse de la capture réseau révèle une séquence d'actions malveillantes orchestrées depuis le poste de **Jean Martin (192.168.10.42)**.

**CHRONOLOGIE DES FAITS :**

• À **14h25**, l'acteur résout le nom du serveur interne `srv-intern01.techcorp.local` (phase de reconnaissance).

• À **14h30**, il ouvre une première session **SSH** vers srv-intern01 (192.168.10.15), d'une durée de 22 minutes, durant laquelle environ 150 Ko de données chiffrées sont échangées — compatible avec l'exécution de scripts de collecte de données.

• À **14h35**, depuis le serveur compromis, une requête DNS résout `ftp.securedrop-ext.com` vers 203.0.113.50 — un domaine externe non référencé dans l'infrastructure TechCorp.

• À **14h36**, une connexion **FTP** est établie depuis srv-intern01 vers ce serveur externe. Les identifiants sont transmis **en clair** : `USER jm_drop / PASS OrionExfil2026!`. Les initiales « jm » correspondent à Jean Martin. Le mot de passe contient le nom du projet ciblé (« Orion ») et le terme « Exfil ».

• Entre **14h38 et 14h48**, le fichier `projet_orion.tar.gz` (4 398 041 octets) est transféré via FTP en mode passif. Le transfert est confirmé par le serveur (226 Transfer complete).

• À **18h05**, trois requêtes **DNS de type TXT** sont émises vers `*.tun.securedrop-ext.com` avec des sous-domaines encodés en Base64. Le décodage révèle : « Projet_Orion », « Budget_2026 », « Plans_Confid » — technique classique de **DNS tunneling**.

• À **18h08**, une tentative de connexion **VPN** (vpn-provider.net) est bloquée par le firewall (RST/ACK).

• À **18h15**, une session HTTPS est établie vers `novatech-industries.com` (198.51.100.25), un **concurrent direct de TechCorp** — possible livraison d'informations ou espionnage industriel.

• À **18h20**, une seconde session SSH (~45 Ko, 8 min 28 sec) est ouverte vers srv-intern01 — pattern compatible avec une opération de **nettoyage** (suppression de logs, effacement de traces).

**CONCLUSION :**
L'ensemble des artefacts réseau constitue un faisceau de preuves convergent vers une **exfiltration de données industrielles par un acteur interne identifié comme Jean Martin**. Les techniques utilisées (SSH pour l'accès, FTP pour l'exfiltration, DNS tunneling pour les métadonnées, et nettoyage post-opératoire) démontrent une action **préméditée et méthodique**.
""")
