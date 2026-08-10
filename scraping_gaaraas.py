"""
Module de collecte et de nettoyage de données, Source : Gaaraas (annonces automobiles, Dakar)
Extraction via Selenium : marque, modèle, année, prix, kilométrage,
type de boîte de vitesses et région de vente pour chaque annonce.
"""

import time
import pandas as pd
from selenium.webdriver.common.by import By

from scraping_books import get_driver  # même driver que pour Books


def scraper_gaaraas(nb_pages: int = 100, progress_callback=None):
    driver = get_driver()
    df_final = pd.DataFrame()

    try:
        for i in range(1, nb_pages + 1):
            url = f"https://www.gaaraas.com/fr/users/dakar-auto?page={i}"
            driver.get(url)
            time.sleep(3)

            containers = driver.find_elements(By.CSS_SELECTOR, "a.common-ad-card")
            print(f"Page {i} : {len(containers)} containers trouvés")

            data = []
            for container in containers:
                try:
                    dic = {
                        "titre_complet": container.find_element(By.CSS_SELECTOR, "h4").get_attribute("textContent").strip(),
                        "Prix": container.find_element(By.CSS_SELECTOR, ".ad-vehicle-price .value").get_attribute("textContent").strip(),
                        "Kilometrage": container.find_element(By.CSS_SELECTOR, ".ad-vehicle-mileage .value").get_attribute("textContent").strip(),
                        "Boite_de_vitesse": container.find_element(By.CSS_SELECTOR, "div.md-hidden").get_attribute("textContent").strip(),
                        "Region_de_vente": container.find_element(By.CSS_SELECTOR, "div.location").get_attribute("textContent").strip(),
                    }
                    data.append(dic)
                except Exception:
                    pass

            df = pd.DataFrame(data)
            df_final = pd.concat([df_final, df], axis=0).reset_index(drop=True)

            if progress_callback:
                progress_callback(i, nb_pages)
    finally:
        driver.quit()

    print(f"df_final shape avant nettoyage : {df_final.shape}")

    df_clean = df_final.copy()
    if not df_clean.empty:
        print("Aperçu brut Prix/Kilometrage :")
        print(df_clean[["Prix", "Kilometrage"]].head(5).to_dict())

        # Nettoyer Prix : ne garder que les chiffres (insensible à la casse et aux espaces)
        df_clean["Prix"] = df_clean["Prix"].str.replace(r"[^\d]", "", regex=True)
        df_clean["Prix"] = pd.to_numeric(df_clean["Prix"], errors="coerce")

        # Nettoyer Kilometrage : ne garder que les chiffres
        df_clean["Kilometrage"] = df_clean["Kilometrage"].str.replace(r"[^\d]", "", regex=True)
        df_clean["Kilometrage"] = pd.to_numeric(df_clean["Kilometrage"], errors="coerce")

        # Supprimer les lignes où Prix ou Kilometrage n'ont pas pu être convertis
        df_clean = df_clean.dropna(subset=["Prix", "Kilometrage"])

        # Extraire Annee
        df_clean["Annee"] = df_clean["titre_complet"].str.extract(r"(\d{4})")
        df_clean = df_clean.dropna(subset=["Annee"]).copy()
        df_clean["Annee"] = df_clean["Annee"].astype(int)

        # Extraire Marque, Modele
        df_clean["Marque"] = df_clean["titre_complet"].str.split(" ").str[0]
        df_clean["Modele"] = df_clean["titre_complet"].str.split(" ", n=2).str[2]

        # Nettoyer Boite_de_vitesse (déduite du texte de description)
        df_clean["Boite_de_vitesse"] = df_clean["Boite_de_vitesse"].str.lower().str.contains("automatique")
        df_clean["Boite_de_vitesse"] = df_clean["Boite_de_vitesse"].map(
            {True: "Automatique", False: "Manuelle"}
        )

        # Ordre final
        df_clean = df_clean[
            ["Marque", "Modele", "Annee", "Prix", "Kilometrage", "Boite_de_vitesse", "Region_de_vente"]
        ]

    print(f"df_clean shape final : {df_clean.shape}")

    return df_final, df_clean