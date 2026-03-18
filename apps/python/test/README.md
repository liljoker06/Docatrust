# OCR traitement

Contenu déplacé depuis le dossier `Aymane` :

- `notebooks/OCR.ipynb` : notebook d'origine
- `scripts/generate_facture_images.py` : génération d'images de factures (datasets OCR)
- `src/ocr_traitement/` : extraction du notebook en scripts Python (pipeline PaddleOCR)

## Exécution (CLI)

Depuis la racine du repo :

```bash
cd "ocr traitement"
# Le package est dans `src/`, donc on ajoute `src` au PYTHONPATH
# Par défaut, le pipeline lit `ocr traitement/facture-images/`.
PYTHONPATH=src python3 -m ocr_traitement --pattern clean
```

Si tes images sont ailleurs :

```bash
cd "ocr traitement"
export FACTURE_IMG_DIR="/chemin/vers/facture-images"
PYTHONPATH=src python3 -m ocr_traitement --pattern clean
```

Fichiers générés (par défaut) :
- `ocr traitement/outputs/annotated.jpg`
- `ocr traitement/outputs/paddleocr_invoice_fields.csv`

## Alternative (installation editable)

```bash
cd "ocr traitement"
python3 -m pip install -e src
python3 -m ocr_traitement --pattern clean
```

## Front de test (Streamlit)

```bash
cd "ocr traitement"
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Onglets :
- **Upload facture (OCR)** : upload image → OCR + export champs + image annotée
- **Recherche Sirene (INSEE)** : lookup SIREN/SIRET

