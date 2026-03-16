import os
import random
import numpy as np
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

# Chemin Poppler
POPPLER_PATH = r"C:\poppler\poppler-25.12.0\Library\bin"

INPUT_DIR  = "data/factures/valides"
OUTPUT_DIR = "data/factures/scans"
os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(42)

def bruiter_image(img):
    """Applique des dégradations aléatoires pour simuler un vrai scan."""

    # 1. Légère rotation (-3° à +3°)
    angle = random.uniform(-3, 3)
    img = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))

    # 2. Réduction de résolution (simulation smartphone)
    if random.random() < 0.5:
        w, h = img.size
        scale = random.uniform(0.5, 0.8)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img = img.resize((w, h), Image.LANCZOS)

    # 3. Flou léger
    if random.random() < 0.6:
        radius = random.uniform(0.5, 1.5)
        img = img.filter(ImageFilter.GaussianBlur(radius=radius))

    # 4. Bruit gaussien
    if random.random() < 0.7:
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, random.uniform(5, 20), arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    # 5. Contraste / luminosité aléatoire
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.7, 1.3))

    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.8, 1.2))

    # 6. Conversion en niveaux de gris (comme un vrai scan)
    if random.random() < 0.5:
        img = img.convert("L").convert("RGB")

    return img

# Traiter toutes les factures
pdfs = sorted(Path(INPUT_DIR).glob("*.pdf"))
print(f"{len(pdfs)} factures trouvées, génération des scans...")

for pdf_path in pdfs:
    pages = convert_from_path(str(pdf_path), dpi=150, poppler_path=POPPLER_PATH)
    
    for i, page in enumerate(pages):
        scan = bruiter_image(page)
        
        nom = pdf_path.stem
        output_path = f"{OUTPUT_DIR}/{nom}_scan.jpg"
        scan.save(output_path, "JPEG", quality=random.randint(60, 90))
    
    print(f"  ✓ {pdf_path.name} → {nom}_scan.jpg")

print(f"\nDone ! {len(pdfs)} scans dans {OUTPUT_DIR}/")