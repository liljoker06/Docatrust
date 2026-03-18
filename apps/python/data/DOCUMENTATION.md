# Documentation — Génération du dataset

## Objectif

Fournir un dataset réaliste et varié pour entraîner et tester le pipeline IA :
classification de documents, OCR sur scans dégradés, détection d'anomalies inter-documents.

---

## Types de documents générés

| Type | Valides | Erronés | Source des données |
|---|---|---|---|
| Factures | 50 | 50 | CSV SIRENE + Faker fr_FR |
| Devis | 30 | 50 | CSV SIRENE + Faker fr_FR |
| RIB | 30 | 50 | CSV SIRENE + Faker fr_FR |
| Attestation SIRET | 30 | 50 | CSV SIRENE + Faker fr_FR |
| Attestation URSSAF | 30 | 50 | CSV SIRENE + Faker fr_FR |
| Extrait Kbis | 30 | 50 | CSV SIRENE + Faker fr_FR |

---

## Anomalies simulées (5 cas × 10 fichiers par type)

### Factures
1. TVA incohérente (taux ne correspond pas au montant)
2. Total TTC faux (HT + TVA ≠ TTC)
3. Date d'échéance antérieure à la date d'émission
4. SIRET invalide (Luhn faux)
5. Numéro de facture manquant

### Devis
1. Remise illogique (> 100%)
2. Total incohérent
3. Date de validité dépassée
4. SIRET invalide
5. Numéro de devis manquant

### RIB
1. Checksum IBAN invalide (ISO 7064)
2. BIC incohérent avec la banque
3. Titulaire ne correspond pas au SIRET
4. Domiciliation étrangère
5. IBAN tronqué

### Attestation SIRET
1. Clé Luhn du SIRET invalide
2. SIRET ne correspond pas au nom de l'entreprise
3. Attestation expirée
4. Code NAF manquant
5. État administratif incohérent (entreprise fermée mais attestation active)

### Attestation URSSAF
1. Attestation expirée
2. SIRET invalide (Luhn faux)
3. Numéro de cotisant manquant
4. Période de validité incohérente
5. Région URSSAF ne correspond pas au département du SIRET

### Extrait Kbis
1. Kbis périmé (délivré il y a > 3 mois)
2. SIREN invalide (Luhn faux)
3. Capital social négatif
4. Section dirigeants vide
5. Forme juridique absente

---

## Scans dégradés

Chaque PDF (valide et erroné) est converti en JPEG simulant un scan réel.  
3 niveaux de dégradation appliqués aléatoirement :

| Niveau | Effets |
|---|---|
| Léger | Légère rotation, bruit faible |
| Moyen | Rotation, flou, bruit, ombres de coin |
| Sévère | Forte rotation, flou gaussien, taches, distorsion perspective |

---

## Architecture technique

- **Génération** : Python + ReportLab (PDFs), pdf2image + Pillow/numpy (scans)
- **Données** : `data/raw/entreprises_sample.csv` (extrait base SIRENE INSEE)
- **API** : FastAPI sur port 8000, un endpoint `POST /generate/<type>` par script
- **Helpers partagés** : `data/scripts/helpers.py` — IBAN/Luhn/SIREN, listes métier
- **Conteneurisation** : Docker (service `hackaton-python`)

---

## Structure des fichiers générés

```
data/
├── raw/                         ← CSV SIRENE source
├── scripts/                     ← Scripts de génération + helpers.py
├── factures/
│   ├── valides/                 ← PDFs propres labellisés OK
│   ├── erronees/                ← PDFs avec anomalies (nommés cas1_..., cas2_...)
│   ├── scans/                   ← Scans JPEG des valides
│   └── scans_erronees/          ← Scans JPEG des erronés
├── devis/ | rib/ | siret/ | urssaf/ | kbis/   ← même structure
```

Les noms de fichiers (`cas1_`, `cas2_`...) et les dossiers (`valides/`, `erronees/`) servent de **labels** pour l'entraînement.
