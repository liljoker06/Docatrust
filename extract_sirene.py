import pandas as pd
import zipfile
import os

# Chemin vers ton zip
ZIP_PATH = "data/StockEtablissement_utf8.zip"
OUTPUT_PATH = "data/entreprises_sample.csv"

# Colonnes utiles pour nos factures
COLONNES = [
    "siret",
    "siren",
    "denominationUniteLegale",
    "nomUniteLegale",
    "prénomUsuelUniteLegale",
    "activitePrincipaleEtablissement",  # code NAF
    "numeroVoieEtablissement",
    "typeVoieEtablissement",
    "libelleVoieEtablissement",
    "codePostalEtablissement",
    "libelleCommuneEtablissement",
    "etatAdministratifEtablissement",   # A = actif
]

print("Ouverture du zip...")

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    # Trouver le fichier CSV dedans
    csv_name = [f for f in z.namelist() if f.endswith('.csv')][0]
    print(f"Fichier trouvé : {csv_name}")
    
    with z.open(csv_name) as f:
        # Lecture par chunks pour ne pas exploser la RAM
        chunks = []
        for chunk in pd.read_csv(f, chunksize=100_000, dtype=str, low_memory=False):
            # Garder uniquement les établissements actifs
            if "etatAdministratifEtablissement" in chunk.columns:
                chunk = chunk[chunk["etatAdministratifEtablissement"] == "A"]
            chunks.append(chunk)
            print(f"  {sum(len(c) for c in chunks):,} établissements actifs lus...")
            # On s'arrête quand on a assez
            if sum(len(c) for c in chunks) >= 5000:
                break

print("Assemblage...")
df = pd.concat(chunks, ignore_index=True)

# Garder uniquement les colonnes qui existent dans le fichier
cols_dispo = [c for c in COLONNES if c in df.columns]
df = df[cols_dispo]

# Garder 500 entreprises avec dénomination + adresse complètes
df = df.dropna(subset=["siret", "codePostalEtablissement", "libelleCommuneEtablissement"])
df = df.sample(n=min(500, len(df)), random_state=42)

df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"\nDone ! {len(df)} entreprises sauvegardées dans {OUTPUT_PATH}")
print(df.head(3))

