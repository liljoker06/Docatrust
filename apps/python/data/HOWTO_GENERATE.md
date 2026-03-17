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
