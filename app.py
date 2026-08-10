"""
Application Streamlit, Projet d'examen Data Collection
Auteur : Khady Cisse
"""

import os
import platform
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from database import init_db, save_data
from scraping_books import scraper_books
from scraping_gaaraas import scraper_gaaraas

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════
st.set_page_config(page_title="Data Collection, Projet Examen", layout="wide")
init_db()

# ═══════════════════════════════════════════════════════
# DÉTECTION LOCAL vs CLOUD
# ═══════════════════════════════════════════════════════
def est_local():
    """Détecte si l'app tourne en local (Windows/Mac) ou sur Streamlit Cloud (Linux)"""
    return platform.system() in ["Windows", "Darwin"]

# ═══════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════
st.title("Projet d'examen, Data Collection")

section = st.sidebar.radio(
    "Navigation",
    ["Scraper", "Données brutes", "Dashboard", "Formulaires"]
)

# ═══════════════════════════════════════════════════════
# SECTION 1 : SCRAPER
# ═══════════════════════════════════════════════════════
if section == "Scraper":
    st.header("Scraper des données")

    source = st.selectbox(
        "Source à scraper",
        ["Books to Scrape", "Gaaraas (annonces auto)"]
    )
    valeur_defaut = 50 if source == "Books to Scrape" else 100
    nb_pages = st.number_input(
        "Nombre de pages à scraper",
        min_value=1,
        max_value=100,
        value=valeur_defaut
    )

    # Affiche le mode détecté
    mode = "🖥️ LOCAL (Selenium actif)" if est_local() else "☁️ CLOUD (CSV pré-scrapés)"
    st.caption(f"Mode détecté : {mode}")

    if st.button("Lancer le scraping"):
        if est_local():
            # ═══════════════════════════════════════
            # MODE LOCAL : Selenium
            # ═══════════════════════════════════════
            with st.spinner(f"Scraping en cours sur {nb_pages} page(s)..."):
                try:
                    if source == "Books to Scrape":
                        df_brut, df_propre = scraper_books(nb_pages)
                    else:
                        df_brut, df_propre = scraper_gaaraas(nb_pages)

                    table_name = "books" if source == "Books to Scrape" else "gaaraas"
                    save_data(df_propre, table_name)

                    st.success(f"✅ Scraping terminé : {len(df_propre)} lignes après nettoyage.")
                    st.subheader("Données nettoyées")
                    st.dataframe(df_propre)

                    # Téléchargement
                    key_suffix = "books" if source == "Books to Scrape" else "gaaraas"
                    csv_data = df_propre.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Télécharger les données nettoyées (CSV)",
                        data=csv_data,
                        file_name=f"{key_suffix}_nettoye.csv",
                        mime="text/csv"
                    )

                except Exception as e:
                    st.error(f"❌ Erreur pendant le scraping : {e}")

        else:
            # ═══════════════════════════════════════
            # MODE CLOUD : CSV pré-scrapés
            # ═══════════════════════════════════════
            with st.spinner("Chargement des données pré-scrapées..."):
                if source == "Books to Scrape":
                    csv_nettoye = "data/books_nettoye.csv"
                    csv_brut = "data/books_raw_webscraper.csv"
                else:
                    csv_nettoye = "data/gaaraas_nettoye.csv"
                    csv_brut = "data/gaaraas_raw_webscraper.csv"

                # Priorité au CSV nettoyé
                if os.path.exists(csv_nettoye):
                    df_propre = pd.read_csv(csv_nettoye)
                    st.success(f"☁️ Mode cloud : {len(df_propre)} lignes chargées depuis le CSV nettoyé.")
                    st.subheader("Données nettoyées")
                    st.dataframe(df_propre)

                    key_suffix = "books" if source == "Books to Scrape" else "gaaraas"
                    csv_data = df_propre.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Télécharger les données nettoyées (CSV)",
                        data=csv_data,
                        file_name=f"{key_suffix}_nettoye.csv",
                        mime="text/csv"
                    )

                elif os.path.exists(csv_brut):
                    df_brut = pd.read_csv(csv_brut)
                    st.info(f"☁️ Mode cloud : {len(df_brut)} lignes chargées depuis le CSV brut.")
                    st.subheader("Données brutes")
                    st.dataframe(df_brut)

                else:
                    st.error("❌ Aucun fichier CSV trouvé.")
                    st.info("📁 Scrapez en local d'abord, puis poussez les fichiers sur GitHub.")

# ═══════════════════════════════════════════════════════
# SECTION 2 : DONNÉES BRUTES
# ═══════════════════════════════════════════════════════
elif section == "Données brutes":
    st.header("Données brutes (scraping no-code)")

    fichier = st.selectbox(
        "Choisir le fichier",
        ["books_raw_webscraper.csv", "gaaraas_raw_webscraper.csv"]
    )
    chemin = f"data/{fichier}"

    try:
        df = pd.read_csv(chemin)
        st.success(f"✅ {len(df)} lignes chargées")
        st.dataframe(df)

        with open(chemin, "rb") as f:
            st.download_button(
                "📥 Télécharger ce fichier",
                data=f,
                file_name=fichier,
                mime="text/csv"
            )
    except FileNotFoundError:
        st.error(f"❌ Fichier introuvable : {chemin}")

# ═══════════════════════════════════════════════════════
# SECTION 3 : DASHBOARD
# ═══════════════════════════════════════════════════════
elif section == "Dashboard":
    st.header("Dashboard des données nettoyées")

    source = st.selectbox(
        "Source à visualiser",
        ["Books to Scrape", "Gaaraas (annonces auto)"]
    )

    # Chargement des données
    if source == "Books to Scrape":
        csv_path = "data/books_nettoye.csv"
    else:
        csv_path = "data/gaaraas_nettoye.csv"

    try:
        df = pd.read_csv(csv_path)
        st.success(f"✅ {len(df)} lignes chargées")
        st.dataframe(df)

        # Graphiques
        if source == "Books to Scrape":
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Répartition des notes")
                if "V5_Note" in df.columns:
                    st.bar_chart(df["V5_Note"].value_counts())
                else:
                    st.info("Colonne 'V5_Note' non disponible")

            with col2:
                st.subheader("Prix par catégorie")
                if "V8_Categorie" in df.columns and "V2_Prix" in df.columns:
                    st.bar_chart(df.groupby("V8_Categorie")["V2_Prix"].mean())
                else:
                    st.info("Colonnes 'V8_Categorie' ou 'V2_Prix' non disponibles")

        else:  # Gaaraas
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Prix moyen par marque")
                if "Marque" in df.columns and "Prix" in df.columns:
                    st.bar_chart(df.groupby("Marque")["Prix"].mean())
                else:
                    st.info("Colonnes 'Marque' ou 'Prix' non disponibles")

            with col2:
                st.subheader("Répartition boîte de vitesses")
                if "Boite_de_vitesse" in df.columns:
                    st.bar_chart(df["Boite_de_vitesse"].value_counts())
                else:
                    st.info("Colonne 'Boite_de_vitesse' non disponible")

    except FileNotFoundError:
        st.error(f"❌ Fichier introuvable : {csv_path}")
        st.info("📁 Scrapez et nettoyez les données d'abord.")

# ═══════════════════════════════════════════════════════
# SECTION 4 : FORMULAIRES
# ═══════════════════════════════════════════════════════
elif section == "Formulaires":
    st.header("Formulaire d'évaluation")
    st.write("Merci de prendre quelques minutes pour évaluer l'application.")

    # Google Forms
    st.subheader("Formulaire Google")
    components.iframe(
        "https://docs.google.com/forms/d/e/1FAIpQLSeg1_RJQljiyZazJzjU93zBBDPWpIJKi7mRKTSJEYF-Xx6Upg/viewform?usp=header",
        height=800
    )
    st.link_button(
        "📝 Ouvrir le formulaire Google dans un nouvel onglet",
        "https://docs.google.com/forms/d/e/1FAIpQLSeg1_RJQljiyZazJzjU93zBBDPWpIJKi7mRKTSJEYF-Xx6Upg/viewform?usp=header"
    )

    st.divider()

    # Kobo
    st.subheader("Formulaire Kobo")
    st.link_button(
        "📝 Remplir le formulaire Kobo",
        "https://ee.kobotoolbox.org/x/hp72tMTu"
    )