"""
Application Streamlit, Projet d'examen Data Collection
Auteur : Khady Cisse
"""

import streamlit as st
import streamlit.components.v1 as components
from database import init_db, save_data
init_db()
import pandas as pd

from scraping_books import scraper_books
from scraping_gaaraas import scraper_gaaraas

st.set_page_config(page_title="Data Collection, Projet Examen", layout="wide")

st.title("Projet d'examen, Data Collection")

# --- Menu de navigation entre les 4 sections ---
section = st.sidebar.radio(
    "Navigation",
    ["Scraper", "Données brutes", "Dashboard", "Formulaires"]
)

if section == "Scraper":
    st.header("Scraper des données")

    source = st.selectbox("Source à scraper", ["Books to Scrape", "Gaaraas (annonces auto)"])
    valeur_defaut = 50 if source == "Books to Scrape" else 100
    nb_pages = st.number_input(
        "Nombre de pages à scraper",
        min_value=1,
        max_value=100,
        value=valeur_defaut
    )

    if st.button("Lancer le scraping"):
        with st.spinner(f"Scraping en cours sur {nb_pages} page(s)..."):
            try:
                if source == "Books to Scrape":
                    df_brut, df_propre = scraper_books(nb_pages)
                else:
                    df_brut, df_propre = scraper_gaaraas(nb_pages)

                table_name = "books" if source == "Books to Scrape" else "gaaraas"
                save_data(df_propre, table_name)

                st.success(f"Scraping terminé : {len(df_propre)} lignes après nettoyage.")

                st.subheader("Données nettoyées")
                st.dataframe(df_propre)

                key_suffix = "books" if source == "Books to Scrape" else "gaaraas"

                st.download_button(
                    "Télécharger les données nettoyées (CSV)",
                    data=df_propre.to_csv(index=False).encode("utf-8"),
                    file_name=f"{key_suffix}_nettoye.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Erreur pendant le scraping : {e}")

elif section == "Données brutes":
    st.header("Données brutes (scraping no-code)")

    fichier = st.selectbox(
        "Choisir le fichier",
        ["books_raw_webscraper.csv", "gaaraas_raw_webscraper.csv"]
    )

    chemin = f"data/{fichier}"

    try:
        df = pd.read_csv(chemin)
        st.dataframe(df)

        with open(chemin, "rb") as f:
            st.download_button(
                "Télécharger ce fichier",
                data=f,
                file_name=fichier,
                mime="text/csv"
            )
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {chemin}")

elif section == "Dashboard":
    st.header("Dashboard des données nettoyées")

    source = st.selectbox("Source à visualiser", ["Books to Scrape", "Gaaraas (annonces auto)"])
    valeur_defaut = 50 if source == "Books to Scrape" else 100
    nb_pages = st.number_input("Nombre de pages à charger", min_value=1, max_value=100, value=valeur_defaut)

    if st.button("Charger les données"):
        with st.spinner("Chargement..."):
            if source == "Books to Scrape":
                _, df = scraper_books(nb_pages)
            else:
                _, df = scraper_gaaraas(nb_pages)

        st.subheader(f"{len(df)} lignes chargées")
        st.dataframe(df)

        if source == "Books to Scrape":
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Répartition des notes")
                st.bar_chart(df["V5_Note"].value_counts())
            with col2:
                st.subheader("Prix par catégorie (moyenne)")
                st.bar_chart(df.groupby("V8_Categorie")["V2_Prix"].mean())
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Prix moyen par marque")
                st.bar_chart(df.groupby("Marque")["Prix"].mean())
            with col2:
                st.subheader("Répartition boîte de vitesses")
                st.bar_chart(df["Boite_de_vitesse"].value_counts())
elif section == "Formulaires":
    st.header("Formulaire d'évaluation")
    st.write("Merci de prendre quelques minutes pour évaluer l'application.")
    components.iframe(
        "https://docs.google.com/forms/d/e/1FAIpQLSeg1_RJQljiyZazJzjU93zBBDPWpIJKi7mRKTSJEYF-Xx6Upg/viewform?usp=header",
        height=800,
        scrolling=True
    )
    st.divider()
    st.subheader("Formulaire Kobo")
    st.link_button("Remplir le formulaire Kobo", "https://ee.kobotoolbox.org/x/hp72tMTu")
