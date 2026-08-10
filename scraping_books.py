"""
Module de collecte et de nettoyage de données, Source : Books to Scrape (books.toscrape.com)
Extraction via Selenium : titre, prix, disponibilité, note, nombre d'avis,
description, catégorie et taxe pour chaque ouvrage du catalogue.
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import shutil
from selenium.webdriver.chrome.service import Service


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
    chromedriver_path = shutil.which("chromedriver")

    options.binary_location = chromium_path
    service = Service(chromedriver_path)

    return webdriver.Chrome(service=service, options=options)

def scraper_books(nb_pages: int = 50, progress_callback=None):
    driver = get_driver()
    df_final = pd.DataFrame()

    try:
        for numero_page in range(1, nb_pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{numero_page}.html"
            driver.get(url)
            time.sleep(2)

            containers = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

            if len(containers) == 0:
                print(f"Fin du catalogue a la page {numero_page}")
                break

            nb_products = len(containers)
            print(f"Page {numero_page}: {nb_products} produits")

            livres_page = []
            for container in containers:
                title = container.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("title")
                price = container.find_element(By.CSS_SELECTOR, "p.price_color").text.replace("£", "")
                aval = container.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
                rating_class = container.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
                rating = rating_class.split()[-1]
                lien = container.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")

                livres_page.append({
                    "title": title, "price": price, "aval": aval,
                    "rating": rating, "lien": lien,
                })

            data = []
            for infos in livres_page:
                try:
                    driver.get(infos["lien"])
                    time.sleep(2)

                    nb_reviews = driver.find_element(
                        By.XPATH,
                        "//th[normalize-space()='Number of reviews']/following-sibling::td",
                    ).text

                    description = driver.find_element(
                        By.XPATH,
                        "//div[@id='product_description']/following-sibling::p",
                    ).text

                    category = driver.find_elements(
                        By.CSS_SELECTOR, ".breadcrumb li a"
                    )[2].text

                    tax = driver.find_element(
                        By.XPATH,
                        "//th[normalize-space()='Tax']/following-sibling::td",
                    ).text

                    dic = {
                        "V1_Titre": infos["title"],
                        "V2_Prix": float(infos["price"]),
                        "V3_Disponibilite": infos["aval"],
                        "V4_Nombre_produits_page": nb_products,
                        "V5_Note": infos["rating"],
                        "V6_Nombre_reviews": nb_reviews,
                        "V7_Description": description,
                        "V8_Categorie": category,
                        "V9_Tax": tax,
                    }
                    data.append(dic)
                except Exception:
                    pass

            df = pd.DataFrame(data)
            df_final = pd.concat([df_final, df], axis=0).reset_index(drop=True)

            if progress_callback:
                progress_callback(numero_page, nb_pages)

        print(f"Termine: {len(df_final)} livres scrapes")
    finally:
        driver.quit()

    def nettoyer_dispo(texte):
        if "in stock" in str(texte).lower():
            return "En stock"
        return "Rupture de stock"

    def nettoyer_note(texte):
        notes = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return notes.get(texte, None)

    def nettoyer_tax(texte):
        texte = str(texte).replace("£", "").strip()
        try:
            return float(texte)
        except ValueError:
            return None

    def nettoyer_reviews(texte):
        try:
            return int(texte)
        except (ValueError, TypeError):
            return 0

    df_propre = df_final.copy()
    if not df_propre.empty:
        df_propre["V3_Disponibilite"] = df_propre["V3_Disponibilite"].apply(nettoyer_dispo)
        df_propre["V5_Note"] = df_propre["V5_Note"].apply(nettoyer_note)
        df_propre["V6_Nombre_reviews"] = df_propre["V6_Nombre_reviews"].apply(nettoyer_reviews)
        df_propre["V9_Tax"] = df_propre["V9_Tax"].apply(nettoyer_tax)

        df_propre = df_propre.drop_duplicates()
        print(f"Nombre de livres apres nettoyage: {len(df_propre)}")

    return df_final, df_propre