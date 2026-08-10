import sqlite3
import pandas as pd

DB_PATH = "data/projet_examen.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            V1_Titre TEXT,
            V2_Prix REAL,
            V3_Disponibilite TEXT,
            V4_Nombre_produits_page INTEGER,
            V5_Note INTEGER,
            V6_Nombre_reviews INTEGER,
            V7_Description TEXT,
            V8_Categorie TEXT,
            V9_Tax REAL,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaaraas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Marque TEXT,
            Modele TEXT,
            Annee INTEGER,
            Prix REAL,
            Kilometrage REAL,
            Boite_de_vitesse TEXT,
            Region_de_vente TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_data(df: pd.DataFrame, table_name: str):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()