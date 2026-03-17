import os
import random
import numpy as np
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

# Chemin Poppler : défini via variable d'environnement pour Windows,
# None sur Linux/Docker (poppler-utils installé en système)
POPPLER_PATH = os.environ.get("POPPLER_PATH", None)

# Dossiers à traiter : (input, output)
DOSSIERS = [
    (os.path.join(DATA_DIR, "factures", "valides"), os.path.join(DATA_DIR, "factures", "scans")),
    (os.path.join(DATA_DIR, "devis", "valides"),    os.path.join(DATA_DIR, "devis", "scans")),
]

random.seed(42)

# Niveaux de dégradation : proba d'apparition et paramètres associés
NIVEAUX = {
    "leger":  0.3,   # 30% des documents → scan quasi propre
    "moyen":  0.4,   # 40% → dégradations modérées
    "severe": 0.3,   # 30% → cas vraiment difficiles
}

def choisir_niveau():
    r = random.random()
    if r < NIVEAUX["leger"]:
        return "leger"
    elif r < NIVEAUX["leger"] + NIVEAUX["moyen"]:
        return "moyen"
    return "severe"

def ajouter_ombre_coin(img):
    """Simule une ombre/pliure dans un coin du document."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    coin = random.choice(["tl", "tr", "bl", "br"])
    taille = random.randint(int(w * 0.1), int(w * 0.25))
    alpha = random.randint(80, 160)
    if coin == "tl":
        pts = [(0, 0), (taille, 0), (0, taille)]
    elif coin == "tr":
        pts = [(w, 0), (w - taille, 0), (w, taille)]
    elif coin == "bl":
        pts = [(0, h), (taille, h), (0, h - taille)]
    else:
        pts = [(w, h), (w - taille, h), (w, h - taille)]
    draw.polygon(pts, fill=(0, 0, 0, alpha))
    return img

def ajouter_tache(img):
    """Ajoute une tache/tampon opaque sur le document."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    nb_taches = random.randint(1, 3)
    for _ in range(nb_taches):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(10, 50)
        couleur = random.choice([(0, 0, 0), (180, 0, 0), (150, 150, 150)])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=couleur)
    return img

def deformer_perspective(img):
    """Simule une photo prise légèrement de biais (transformation affine)."""
    w, h = img.size
    decalage = random.randint(int(w * 0.03), int(w * 0.08))
    cote = random.choice(["gauche", "droite", "haut", "bas"])
    if cote == "gauche":
        coeffs = (1, 0, 0,  decalage / h, 1, -decalage / 2,  0, 0)
    elif cote == "droite":
        coeffs = (1, 0, 0, -decalage / h, 1,  decalage / 2,  0, 0)
    elif cote == "haut":
        coeffs = (1, decalage / w, -decalage / 2,  0, 1, 0,  0, 0)
    else:
        coeffs = (1, -decalage / w, decalage / 2,  0, 1, 0,  0, 0)
    return img.transform((w, h), Image.AFFINE, coeffs[:6], resample=Image.BICUBIC)

def bruiter_image(img, niveau):
    """Applique des dégradations selon le niveau choisi."""
    w, h = img.size

    # --- Rotation ---
    plages = {"leger": (-1, 1), "moyen": (-3, 3), "severe": (-7, 7)}
    angle = random.uniform(*plages[niveau])
    img = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))

    # --- Réduction de résolution (simulation smartphone/fax) ---
    probas = {"leger": 0.2, "moyen": 0.5, "severe": 0.9}
    if random.random() < probas[niveau]:
        scales = {"leger": (0.75, 0.95), "moyen": (0.5, 0.8), "severe": (0.25, 0.5)}
        scale = random.uniform(*scales[niveau])
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img = img.resize((w, h), Image.LANCZOS)

    # --- Flou ---
    probas = {"leger": 0.3, "moyen": 0.6, "severe": 1.0}
    if random.random() < probas[niveau]:
        radii = {"leger": (0.3, 0.8), "moyen": (0.8, 2.0), "severe": (2.0, 4.5)}
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(*radii[niveau])))

    # --- Bruit gaussien ---
    probas = {"leger": 0.3, "moyen": 0.7, "severe": 1.0}
    if random.random() < probas[niveau]:
        intensites = {"leger": (2, 8), "moyen": (8, 25), "severe": (25, 55)}
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, random.uniform(*intensites[niveau]), arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    # --- Contraste / luminosité ---
    plages_c = {"leger": (0.85, 1.15), "moyen": (0.6, 1.4), "severe": (0.3, 1.8)}
    plages_b = {"leger": (0.9, 1.1),  "moyen": (0.7, 1.3), "severe": (0.4, 1.7)}
    img = ImageEnhance.Contrast(img).enhance(random.uniform(*plages_c[niveau]))
    img = ImageEnhance.Brightness(img).enhance(random.uniform(*plages_b[niveau]))

    # --- Niveaux de gris ---
    probas = {"leger": 0.3, "moyen": 0.6, "severe": 0.85}
    if random.random() < probas[niveau]:
        img = img.convert("L").convert("RGB")

    # --- Ombre de coin (moyen/sévère) ---
    if niveau in ("moyen", "severe") and random.random() < 0.4:
        img = ajouter_ombre_coin(img)

    # --- Tache/tampon (sévère uniquement) ---
    if niveau == "severe" and random.random() < 0.5:
        img = ajouter_tache(img)

    # --- Déformation perspective (moyen/sévère) ---
    probas = {"moyen": 0.3, "severe": 0.6}
    if niveau in probas and random.random() < probas[niveau]:
        img = deformer_perspective(img)

    return img

# Traiter chaque dossier (factures valides + devis valides)
for INPUT_DIR, OUTPUT_DIR in DOSSIERS:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdfs = sorted(Path(INPUT_DIR).glob("*.pdf"))
    label = os.path.basename(os.path.dirname(INPUT_DIR))  # "factures" ou "devis"
    print(f"\n[{label}] {len(pdfs)} fichiers trouvés, génération des scans...")

    for pdf_path in pdfs:
        niveau = choisir_niveau()
        pages = convert_from_path(str(pdf_path), dpi=150, poppler_path=POPPLER_PATH)

        for page in pages:
            scan = bruiter_image(page, niveau)
            nom = pdf_path.stem
            # Le niveau est inclus dans le nom pour traçabilité
            output_path = os.path.join(OUTPUT_DIR, f"{nom}_{niveau}_scan.jpg")
            scan.save(output_path, "JPEG", quality=random.randint(55, 90))

        print(f"  ✓ {pdf_path.name} → [{niveau}] {nom}_{niveau}_scan.jpg")

    print(f"Done ! {len(pdfs)} scans dans {OUTPUT_DIR}/")