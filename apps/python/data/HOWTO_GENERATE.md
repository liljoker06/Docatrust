# Générer le dataset complet

## Prérequis
- Docker Desktop lancé
- Avoir fait `git pull` sur la branche `marwanG12`

## 1. Démarrer les conteneurs
```bash
docker-compose up -d
```
Attendre que le service `hackaton-python` soit up (port 8000).

## 2. Générer tous les documents PDF

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/factures"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/factures-erronees"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/devis"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/devis-erronees"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/rib"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/rib-erronees"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/siret"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/siret-erronees"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/urssaf"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/urssaf-erronees"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/kbis"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/kbis-erronees"
```

## 3. Générer les scans (JPEG dégradés)
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/scans"
```
> Cette étape convertit tous les PDFs en images simulant des scans de mauvaise qualité.  
> Elle est longue (~2-3 min), attendre le retour `status: ok`.

## 4. Générer le manifeste du dataset
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/generate/manifest"
```
> Génère `data/dataset_manifest.csv` — un fichier listant tous les fichiers du dataset avec leurs labels.  
> À régénérer après chaque appel à `/generate/scans`.

Le manifeste est directement exploitable en Python :
```python
import pandas as pd
df = pd.read_csv("data/dataset_manifest.csv")
# colonnes : fichier, type, label, anomalie, format
```

## Résultat attendu

```
data/
├── factures/   valides/ (50) | erronees/ (50) | scans/ | scans_erronees/
├── devis/      valides/ (30) | erronees/ (50) | scans/ | scans_erronees/
├── rib/        valides/ (30) | erronees/ (50) | scans/ | scans_erronees/
├── siret/      valides/ (30) | erronees/ (50) | scans/ | scans_erronees/
├── urssaf/     valides/ (30) | erronees/ (50) | scans/ | scans_erronees/
└── kbis/       valides/ (30) | erronees/ (50) | scans/ | scans_erronees/
```

Total : ~270 PDFs + leurs scans JPEG (3 niveaux de dégradation aléatoires).
