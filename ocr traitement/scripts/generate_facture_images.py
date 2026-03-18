#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facture Image Generator - Generates realistic test invoice images from texte de facture files.
Creates multiple quality variations for OCR testing and document recognition systems.
"""

import os
import re
import glob
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Configuration
FACTURETXT_DIR = "/Users/aymanehajli/Desktop/IPSSI/M2/HACKATHON/Aymane/facturetxt"
OUTPUT_DIR = "/Users/aymanehajli/Desktop/IPSSI/M2/HACKATHON/Aymane/output/facture-images"
MANIFEST_FILE = os.path.join(OUTPUT_DIR, "manifest.txt")

# Image settings
IMG_WIDTH = 1200
IMG_HEIGHT = 1600  # A4-like ratio
MARGIN = 60
LINE_HEIGHT = 32
TABLE_CELL_PADDING = 8

# Quality variations - multiple levels for comprehensive testing
QUALITY_VARIANTS = [
    ("clean", "high", "Clean high-resolution image"),
    ("semi_blur", "medium", "Semi-blurred image with slight motion/focus issues"),
    ("phone_capture", "medium", "Phone-captured image with rotation and lighting effects"),
    ("rotation", "medium", "Rotated scan (deskew needed)"),
    ("low_quality", "low", "Low-quality JPEG compression + noise"),
]

DEFAULT_TEMPLATE = os.environ.get("FACTURE_TEMPLATE", "classic")
# Multiple designs in one run:
# - FACTURE_TEMPLATES=all
# - FACTURE_TEMPLATES=classic,boxed,modern
TEMPLATE_SET = os.environ.get("FACTURE_TEMPLATES", DEFAULT_TEMPLATE)
SYNTHETIC_COUNT = int(os.environ.get("SYNTHETIC_COUNT", "0"))  # if >0, generate faker invoices too
# If true, generate ONLY ONE random (template+quality) per invoice
ONE_RANDOM_PER_INVOICE = os.environ.get("ONE_RANDOM_PER_INVOICE", "0").strip() in ("1", "true", "True", "yes", "y")


@dataclass
class TemplateSpec:
    name: str
    render_image: Callable[[Dict], Image.Image]


def parse_facture_file(filepath):
    """Parse a facture texte file and extract key information."""
    data = {
        "invoice_number": "",
        "date_emission": "",
        "date_echeance": "",
        "supplier": {},
        "client": {},
        "line_items": [],
        "totals": {},
        "payment_conditions": [],
        "bank_info": {},
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract invoice number
        match = re.search(r"FACTURE N°\s*(FAC-\d+-\d+)", content)
        if match:
            data["invoice_number"] = match.group(1)

        # Extract dates (handle bold markdown format **Date d'émission:**)
        match = re.search(r"\*{0,2}Date d'émission:\*{0,2}\s*(\d+/\d+/\d+)", content)
        if match:
            data["date_emission"] = match.group(1)

        match = re.search(r"\*{0,2}Date d'échéance:\*{0,2}\s*(\d+/\d+/\d+)", content)
        if match:
            data["date_echeance"] = match.group(1)

        # Extract supplier info
        supplier_section = re.search(r"## FOURNISSEUR.*?## CLIENT", content, re.DOTALL)
        if supplier_section:
            supplier_text = supplier_section.group(0)
            data["supplier"]["name"] = extract_table_value(supplier_text, "Raison sociale")
            data["supplier"]["address"] = extract_table_value(supplier_text, "Adresse")
            data["supplier"]["city"] = extract_table_value(supplier_text, "Code postal / Ville")
            data["supplier"]["phone"] = extract_table_value(supplier_text, "Téléphone")
            data["supplier"]["email"] = extract_table_value(supplier_text, "Email")
            data["supplier"]["siret"] = extract_table_value(supplier_text, "SIRET")
            data["supplier"]["tva"] = extract_table_value(supplier_text, "TVA Intracommunautaire")

        # Extract client info
        client_section = re.search(r"## CLIENT.*?## DÉTAILS", content, re.DOTALL)
        if client_section:
            client_text = client_section.group(0)
            data["client"]["name"] = extract_table_value(client_text, "Raison sociale")
            data["client"]["address"] = extract_table_value(client_text, "Adresse")
            data["client"]["city"] = extract_table_value(client_text, "Code postal / Ville")
            data["client"]["phone"] = extract_table_value(client_text, "Téléphone")
            data["client"]["email"] = extract_table_value(client_text, "Email")
            data["client"]["siret"] = extract_table_value(client_text, "SIRET")
            data["client"]["tva"] = extract_table_value(client_text, "TVA Intracommunautaire")

        # Extract line items - parse rows with € symbol
        # Match rows like: | LOC-001 | Description | Qté | Price | Total |
        item_rows = re.findall(r"\|[ ]*([A-Z]{3}-\d{3})\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|", content)
        for row in item_rows:
            data["line_items"].append({
                "ref": row[0].strip(),
                "description": row[1].strip(),
                "quantity": row[2].strip(),
                "unit_price": row[3].strip(),
                "total": row[4].strip(),
            })

        # Extract totals - handle bold markdown formatting
        totals_section = re.search(r"## TOTAUX[\s\S]*?## CONDITIONS", content)
        if totals_section:
            totals_text = totals_section.group(0)
            # Extract Total HT - handle bold formatting
            ht_match = re.search(r"\*\*Total HT.*?\*\*\s*\|\s*\*\*([\d\s.,]+€)\*\*", totals_text)
            if ht_match:
                data["totals"]["ht"] = ht_match.group(1).strip()
            # Extract TVA
            tva_match = re.search(r"TVA.*?\|\s*([\d\s.,]+€)", totals_text)
            if tva_match:
                data["totals"]["tva"] = tva_match.group(1).strip()
            # Extract Total TTC - handle bold formatting
            ttc_match = re.search(r"\*\*Total TTC.*?\*\*\s*\|\s*\*\*([\d\s.,]+€)\*\*", totals_text)
            if ttc_match:
                data["totals"]["ttc"] = ttc_match.group(1).strip()

        # Extract bank info - search entire content for bank data row
        bank_match = re.search(r"\|[ ]*LCL\s*\|([^|]+)\|([^|]+)\|", content)
        if bank_match:
            data["bank_info"]["bank"] = "LCL"
            data["bank_info"]["bic"] = bank_match.group(1).strip()
            data["bank_info"]["iban"] = bank_match.group(2).strip()

        data["source_file"] = os.path.basename(filepath)

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        data["error"] = str(e)

    return data


def extract_table_value(text, key_pattern):
    """Extract value from markdown table based on key."""
    # Handle bold markdown formatting (**key**) and regular keys
    pattern = rf"\|\s*\*{{0,2}}{key_pattern}\*{{0,2}}\s*\|\s*([^|]+)\|"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def get_font(font_size=16, bold=False):
    """Get a font, falling back to default if custom fonts unavailable."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/dejavusans.ttf",
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except:
                pass

    # Fall back to default
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", font_size)

def _try_get_faker(locale: str = "fr_FR"):
    """Return a Faker instance or None if not installed."""
    try:
        from faker import Faker  # type: ignore
    except Exception:
        return None
    fk = Faker(locale)
    fk.seed_instance(42)
    return fk


def generate_synthetic_facture_data(count: int = 10) -> List[Dict]:
    """Generate synthetic invoice data using Faker for realistic templates."""
    fk = _try_get_faker("fr_FR")
    if fk is None:
        print("Faker not installed. Run: pip install faker")
        return []

    out: List[Dict] = []
    for i in range(count):
        inv_num = f"FAC-2026-{str(i+1).zfill(3)}"
        supplier_company = fk.company()
        client_company = fk.company()

        supplier_phone = fk.phone_number()
        client_phone = fk.phone_number()

        # Normalize phone to French-like spacing if possible
        supplier_phone = re.sub(r"[^\d]", "", supplier_phone)[-10:]
        supplier_phone = " ".join([supplier_phone[j:j+2] for j in range(0, len(supplier_phone), 2)]) if len(supplier_phone) == 10 else supplier_phone
        client_phone = re.sub(r"[^\d]", "", client_phone)[-10:]
        client_phone = " ".join([client_phone[j:j+2] for j in range(0, len(client_phone), 2)]) if len(client_phone) == 10 else client_phone

        def fake_siret():
            # 14 digits grouped like "123 456 789 00012"
            digits = "".join(str(fk.random_int(0, 9)) for _ in range(14))
            return f"{digits[0:3]} {digits[3:6]} {digits[6:9]} {digits[9:14]}"

        supplier_siret = fake_siret()
        client_siret = fake_siret()

        supplier_email = fk.company_email()
        client_email = fk.email()

        supplier_siret_digits = re.sub(r"\s+", "", supplier_siret)
        client_siret_digits = re.sub(r"\s+", "", client_siret)
        supplier_tva = f"FR {fk.random_int(10,99)} {supplier_siret_digits[:9]}"
        client_tva = f"FR {fk.random_int(10,99)} {client_siret_digits[:9]}"

        # Line items
        line_items = []
        n_items = fk.random_int(3, 6)
        total_ht_val = 0.0
        for k in range(n_items):
            ref = f"{fk.random_element(elements=('AUD','LOG','FOR','CONS'))}-{str(k+1).zfill(3)}"
            qty = fk.random_int(1, 15)
            unit = float(fk.random_int(50, 1200))
            total = unit * qty
            total_ht_val += total
            line_items.append({
                "ref": ref,
                "description": fk.sentence(nb_words=5).rstrip("."),
                "quantity": str(qty),
                "unit_price": f"{unit:,.2f} €".replace(",", " ").replace(".", ","),
                "total": f"{total:,.2f} €".replace(",", " ").replace(".", ","),
            })

        tva_rate = 0.20
        tva_val = total_ht_val * tva_rate
        total_ttc_val = total_ht_val + tva_val

        data = {
            "invoice_number": inv_num,
            "date_emission": fk.date_between(start_date="-30d", end_date="today").strftime("%d/%m/%Y"),
            "date_echeance": fk.date_between(start_date="today", end_date="+45d").strftime("%d/%m/%Y"),
            "supplier": {
                "name": supplier_company,
                "address": fk.street_address(),
                "city": f"{fk.postcode()} {fk.city().upper()}",
                "phone": supplier_phone,
                "email": supplier_email,
                "siret": supplier_siret,
                "tva": supplier_tva,
            },
            "client": {
                "name": client_company,
                "address": fk.street_address(),
                "city": f"{fk.postcode()} {fk.city().upper()}",
                "phone": client_phone,
                "email": client_email,
                "siret": client_siret,
                "tva": client_tva,
            },
            "line_items": line_items,
            "totals": {
                "ht": f"{total_ht_val:,.2f} €".replace(",", " ").replace(".", ","),
                "tva": f"{tva_val:,.2f} €".replace(",", " ").replace(".", ","),
                "ttc": f"{total_ttc_val:,.2f} €".replace(",", " ").replace(".", ","),
            },
            "payment_conditions": [
                "Paiement à 45 jours fin de mois",
            ],
            "bank_info": {
                "bank": fk.random_element(elements=("LCL", "Société Générale", "BNP Paribas", "Crédit Agricole")),
                "bic": fk.swift11(),
                "iban": fk.iban(),
            },
            "source_file": "synthetic_faker",
        }
        out.append(data)
    return out


def render_template_classic_image(data: Dict) -> Image.Image:
    """Classic template (current layout) as PIL image."""
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = get_font(24, bold=True)
    section_font = get_font(16, bold=True)
    normal_font = get_font(14)
    small_font = get_font(12)

    y = MARGIN

    # Header - Invoice title
    invoice_num = data.get("invoice_number", "FACTURE")
    draw.text((MARGIN, y), f"FACTURE N° {invoice_num}", font=title_font, fill="#1a1a1a")
    y += 50

    # Dates
    date_emission = data.get("date_emission", "")
    date_echeance = data.get("date_echeance", "")
    draw.text((MARGIN, y), f"Date d'émission: {date_emission}", font=normal_font, fill="#333")
    y += LINE_HEIGHT
    draw.text((MARGIN, y), f"Date d'échéance: {date_echeance}", font=normal_font, fill="#333")
    y += 40

    # Supplier section
    y = draw_supplier_section(draw, data.get("supplier", {}), y, section_font, normal_font)
    y += 20

    # Client section
    y = draw_client_section(draw, data.get("client", {}), y, section_font, normal_font)
    y += 40

    # Line items table
    y = draw_line_items(draw, data.get("line_items", []), y, section_font, normal_font, small_font)
    y += 40

    # Totals
    y = draw_totals(draw, data.get("totals", {}), y, section_font, normal_font)
    y += 40

    # Bank info
    y = draw_bank_info(draw, data.get("bank_info", {}), y, section_font, normal_font)

    # Footer disclaimer
    draw.text(
        (MARGIN, IMG_HEIGHT - 60),
        "FACTURE EXEMPLE - DOCUMENT NON VALIDE - Généré pour test OCR",
        font=small_font,
        fill="#888",
    )

    return img


def render_template_boxed_image(data: Dict) -> Image.Image:
    """A more 'realistic template' layout using boxed header blocks (supplier/client) to help layout detection."""
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    title_font = get_font(26, bold=True)
    section_font = get_font(16, bold=True)
    normal_font = get_font(14)
    small_font = get_font(12)

    y = MARGIN
    invoice_num = data.get("invoice_number", "FACTURE")
    draw.text((MARGIN, y), f"FACTURE N° {invoice_num}", font=title_font, fill="#1a1a1a")

    # Right box: dates
    box_w = 420
    box_h = 90
    x_box = IMG_WIDTH - MARGIN - box_w
    draw.rectangle([x_box, y, x_box + box_w, y + box_h], outline="#1a1a1a", width=2)
    draw.text((x_box + 12, y + 10), f"Date d'émission: {data.get('date_emission','')}", font=normal_font, fill="#333")
    draw.text((x_box + 12, y + 42), f"Date d'échéance: {data.get('date_echeance','')}", font=normal_font, fill="#333")
    y += 120

    # Supplier + client boxes side by side
    col_gap = 30
    col_w = (IMG_WIDTH - 2*MARGIN - col_gap) // 2
    box_h = 200
    x1 = MARGIN
    x2 = MARGIN + col_w + col_gap
    draw.rectangle([x1, y, x1 + col_w, y + box_h], outline="#1a1a1a", width=2)
    draw.rectangle([x2, y, x2 + col_w, y + box_h], outline="#1a1a1a", width=2)
    draw.text((x1 + 10, y + 10), "FOURNISSEUR", font=section_font, fill="#1a1a1a")
    draw.text((x2 + 10, y + 10), "CLIENT", font=section_font, fill="#1a1a1a")

    def draw_lines(x, y0, lines):
        yy = y0
        for ln in lines:
            if ln:
                draw.text((x, yy), ln, font=normal_font, fill="#333")
                yy += LINE_HEIGHT
        return yy

    sup = data.get("supplier", {})
    cli = data.get("client", {})
    sup_lines = [
        sup.get("name",""),
        sup.get("address",""),
        sup.get("city",""),
        f"Tél: {sup.get('phone','')}",
        f"Email: {sup.get('email','')}",
        f"SIRET: {sup.get('siret','')}",
        f"TVA: {sup.get('tva','')}",
    ]
    cli_lines = [
        cli.get("name",""),
        cli.get("address",""),
        cli.get("city",""),
        f"Tél: {cli.get('phone','')}",
        f"Email: {cli.get('email','')}",
        f"SIRET: {cli.get('siret','')}",
        f"TVA: {cli.get('tva','')}",
    ]
    draw_lines(x1 + 10, y + 45, sup_lines)
    draw_lines(x2 + 10, y + 45, cli_lines)

    y += box_h + 30
    y = draw_line_items(draw, data.get("line_items", []), y, section_font, normal_font, small_font)
    y += 30
    y = draw_totals(draw, data.get("totals", {}), y, section_font, normal_font)
    y += 30
    y = draw_bank_info(draw, data.get("bank_info", {}), y, section_font, normal_font)

    draw.text(
        (MARGIN, IMG_HEIGHT - 60),
        "FACTURE EXEMPLE - DOCUMENT NON VALIDE - Généré pour test OCR",
        font=small_font,
        fill="#888",
    )

    return img


def render_template_modern_image(data: Dict) -> Image.Image:
    """Modern design template (different header band + boxed totals)."""
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    title_font = get_font(28, bold=True)
    section_font = get_font(16, bold=True)
    normal_font = get_font(14)
    small_font = get_font(12)

    # Header band
    band_h = 120
    draw.rectangle([0, 0, IMG_WIDTH, band_h], fill="#0f766e")
    invoice_num = data.get("invoice_number", "FACTURE")
    draw.text((MARGIN, 30), f"FACTURE • {invoice_num}", font=title_font, fill="white")
    draw.text((IMG_WIDTH - MARGIN - 420, 28), f"Émission: {data.get('date_emission','')}", font=normal_font, fill="white")
    draw.text((IMG_WIDTH - MARGIN - 420, 60), f"Échéance: {data.get('date_echeance','')}", font=normal_font, fill="white")

    y = band_h + 30

    # Supplier / Client cards
    col_gap = 30
    col_w = (IMG_WIDTH - 2 * MARGIN - col_gap) // 2
    card_h = 220
    x1 = MARGIN
    x2 = MARGIN + col_w + col_gap
    for x, label in [(x1, "FOURNISSEUR"), (x2, "CLIENT")]:
        draw.rectangle([x, y, x + col_w, y + card_h], outline="#0f766e", width=2)
        draw.rectangle([x, y, x + col_w, y + 36], fill="#ccfbf1")
        draw.text((x + 10, y + 8), label, font=section_font, fill="#134e4a")

    sup = data.get("supplier", {})
    cli = data.get("client", {})
    sup_lines = [
        sup.get("name", ""),
        sup.get("address", ""),
        sup.get("city", ""),
        f"Tél: {sup.get('phone','')}",
        f"Email: {sup.get('email','')}",
        f"SIRET: {sup.get('siret','')}",
        f"TVA: {sup.get('tva','')}",
    ]
    cli_lines = [
        cli.get("name", ""),
        cli.get("address", ""),
        cli.get("city", ""),
        f"Tél: {cli.get('phone','')}",
        f"Email: {cli.get('email','')}",
        f"SIRET: {cli.get('siret','')}",
        f"TVA: {cli.get('tva','')}",
    ]

    def draw_lines(x, y0, lines):
        yy = y0
        for ln in lines:
            if ln:
                draw.text((x, yy), ln, font=normal_font, fill="#1a1a1a")
                yy += LINE_HEIGHT
        return yy

    draw_lines(x1 + 10, y + 50, sup_lines)
    draw_lines(x2 + 10, y + 50, cli_lines)
    y += card_h + 30

    y = draw_line_items(draw, data.get("line_items", []), y, section_font, normal_font, small_font)
    y += 20

    # Totals box on right
    totals = data.get("totals", {})
    box_w, box_h = 360, 120
    x_box = IMG_WIDTH - MARGIN - box_w
    draw.rectangle([x_box, y, x_box + box_w, y + box_h], outline="#0f766e", width=2)
    draw.rectangle([x_box, y, x_box + box_w, y + 36], fill="#ccfbf1")
    draw.text((x_box + 10, y + 8), "TOTAUX", font=section_font, fill="#134e4a")
    yy = y + 46
    for label, value in [("Total HT:", totals.get("ht", "")), ("TVA:", totals.get("tva", "")), ("Total TTC:", totals.get("ttc", ""))]:
        draw.text((x_box + 10, yy), label, font=normal_font, fill="#333")
        draw.text((x_box + 180, yy), value, font=normal_font, fill="#1a1a1a")
        yy += LINE_HEIGHT

    # Bank info lower-left
    y2 = y + box_h + 20
    _ = draw_bank_info(draw, data.get("bank_info", {}), y2, section_font, normal_font)

    draw.text((MARGIN, IMG_HEIGHT - 60), "FACTURE EXEMPLE - DOCUMENT NON VALIDE - Généré pour test OCR", font=small_font, fill="#888")
    return img


TEMPLATES: Dict[str, TemplateSpec] = {
    "classic": TemplateSpec(name="classic", render_image=render_template_classic_image),
    "boxed": TemplateSpec(name="boxed", render_image=render_template_boxed_image),
    "modern": TemplateSpec(name="modern", render_image=render_template_modern_image),
}


def _resolve_templates() -> List[TemplateSpec]:
    raw = (TEMPLATE_SET or DEFAULT_TEMPLATE or "classic").strip().lower()
    if raw in ("all", "*"):
        return list(TEMPLATES.values())
    names = [x.strip().lower() for x in raw.split(",") if x.strip()]
    specs: List[TemplateSpec] = []
    for n in names:
        if n in TEMPLATES:
            specs.append(TEMPLATES[n])
        else:
            print(f"[WARN] Unknown template '{n}', skipping. Available: {', '.join(TEMPLATES.keys())}")
    return specs or [TEMPLATES["classic"]]


def _apply_quality_variant(base_img: Image.Image, quality_type: str) -> Tuple[Image.Image, Dict]:
    """Return transformed image + save params dict."""
    img = base_img.copy()
    params = {"format": "JPEG", "quality": 95, "dpi": (300, 300)}
    if quality_type == "clean":
        return img, params
    if quality_type == "semi_blur":
        img = apply_blur_degradation(img)
        params.update({"quality": 70, "dpi": (150, 150)})
        return img, params
    if quality_type == "phone_capture":
        img = apply_poor_degradation(img)
        img = img.rotate(3, resample=Image.BICUBIC, expand=False, fillcolor="white")
        params.update({"quality": 60, "dpi": (120, 120)})
        return img, params
    if quality_type == "rotation":
        img = apply_medium_degradation(img)
        img = img.rotate(2.5, resample=Image.BICUBIC, expand=False, fillcolor="white")
        params.update({"quality": 80, "dpi": (200, 200)})
        return img, params
    if quality_type == "low_quality":
        img = apply_poor_degradation(img)
        params.update({"quality": 35, "dpi": (96, 96)})
        return img, params
    img = apply_medium_degradation(img)
    params.update({"quality": 80, "dpi": (200, 200)})
    return img, params


def create_clean_image(data, output_path):
    """Create a clean, high-quality invoice image."""
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = get_font(24, bold=True)
    section_font = get_font(16, bold=True)
    normal_font = get_font(14)
    small_font = get_font(12)

    y = MARGIN

    # Header - Invoice title
    invoice_num = data.get("invoice_number", "FACTURE")
    draw.text((MARGIN, y), f"FACTURE N° {invoice_num}", font=title_font, fill="#1a1a1a")
    y += 50

    # Dates
    date_emission = data.get("date_emission", "")
    date_echeance = data.get("date_echeance", "")
    draw.text((MARGIN, y), f"Date d'émission: {date_emission}", font=normal_font, fill="#333")
    y += LINE_HEIGHT
    draw.text((MARGIN, y), f"Date d'échéance: {date_echeance}", font=normal_font, fill="#333")
    y += 40

    # Supplier section
    y = draw_supplier_section(draw, data.get("supplier", {}), y, section_font, normal_font)
    y += 20

    # Client section
    y = draw_client_section(draw, data.get("client", {}), y, section_font, normal_font)
    y += 40

    # Line items table
    y = draw_line_items(draw, data.get("line_items", []), y, section_font, normal_font, small_font)
    y += 40

    # Totals
    y = draw_totals(draw, data.get("totals", {}), y, section_font, normal_font)
    y += 40

    # Bank info
    y = draw_bank_info(draw, data.get("bank_info", {}), y, section_font, normal_font)

    # Footer disclaimer
    draw.text(
        (MARGIN, IMG_HEIGHT - 60),
        "FACTURE EXEMPLE - DOCUMENT NON VALIDE - Généré pour test OCR",
        font=small_font,
        fill="#888"
    )

    # Save as high-quality JPEG
    img.save(output_path, "JPEG", quality=95, dpi=(300, 300))
    return output_path


def draw_supplier_section(draw, supplier, y, section_font, normal_font):
    """Draw supplier information section."""
    draw.text((MARGIN, y), "FOURNISSEUR", font=section_font, fill="#1a1a1a")
    y += LINE_HEIGHT + 4

    lines = [
        supplier.get("name", ""),
        supplier.get("address", ""),
        supplier.get("city", ""),
        f"Tél: {supplier.get('phone', '')}",
        f"Email: {supplier.get('email', '')}",
        f"SIRET: {supplier.get('siret', '')}",
        f"TVA: {supplier.get('tva', '')}",
    ]

    for line in lines:
        if line:
            draw.text((MARGIN + 10, y), line, font=normal_font, fill="#333")
            y += LINE_HEIGHT

    return y


def draw_client_section(draw, client, y, section_font, normal_font):
    """Draw client information section."""
    draw.text((MARGIN, y), "CLIENT", font=section_font, fill="#1a1a1a")
    y += LINE_HEIGHT + 4

    lines = [
        client.get("name", ""),
        client.get("address", ""),
        client.get("city", ""),
    ]

    for line in lines:
        if line:
            draw.text((MARGIN + 10, y), line, font=normal_font, fill="#333")
            y += LINE_HEIGHT

    return y


def draw_line_items(draw, items, y, section_font, normal_font, small_font):
    """Draw line items table."""
    draw.text((MARGIN, y), "DÉTAILS DES PRESTATIONS", font=section_font, fill="#1a1a1a")
    y += LINE_HEIGHT + 8

    # Table header
    headers = ["Réf", "Description", "Qté", "Prix Unit.", "Total"]
    col_widths = [80, 400, 100, 150, 150]
    x = MARGIN

    # Header background
    draw.rectangle([MARGIN, y, IMG_WIDTH - MARGIN, y + LINE_HEIGHT + 8], fill="#f0f0f0")

    for i, header in enumerate(headers):
        draw.text((x + 5, y + 4), header, font=normal_font, fill="#1a1a1a")
        x += col_widths[i]

    y += LINE_HEIGHT + 12

    # Data rows
    for item in items:
        x = MARGIN
        draw.text((x + 5, y + 2), item.get("ref", ""), font=small_font, fill="#333")
        x += col_widths[0]
        draw.text((x + 5, y + 2), item.get("description", ""), font=small_font, fill="#333")
        x += col_widths[1]
        draw.text((x + 5, y + 2), item.get("quantity", ""), font=small_font, fill="#333")
        x += col_widths[2]
        draw.text((x + 5, y + 2), item.get("unit_price", ""), font=small_font, fill="#333")
        x += col_widths[3]
        draw.text((x + 5, y + 2), item.get("total", ""), font=small_font, fill="#333")
        y += LINE_HEIGHT + 4

        # Row separator
        draw.line((MARGIN, y, IMG_WIDTH - MARGIN, y), fill="#e0e0e0", width=1)
        y += 4

    return y


def draw_totals(draw, totals, y, section_font, normal_font):
    """Draw totals section."""
    draw.text((MARGIN, y), "TOTAUX", font=section_font, fill="#1a1a1a")
    y += LINE_HEIGHT + 8

    # Right-align totals
    x_start = IMG_WIDTH - MARGIN - 250

    totals_items = [
        ("Total HT:", totals.get("ht", "")),
        ("TVA:", totals.get("tva", "")),
        ("Total TTC:", totals.get("ttc", "")),
    ]

    for label, value in totals_items:
        if value:
            draw.text((x_start, y), label, font=normal_font, fill="#333")
            draw.text((x_start + 180, y), value, font=normal_font, fill="#1a1a1a")
            y += LINE_HEIGHT

    return y


def draw_bank_info(draw, bank_info, y, section_font, normal_font):
    """Draw bank information section."""
    draw.text((MARGIN, y), "COORDONNÉES BANCAIRES", font=section_font, fill="#1a1a1a")
    y += LINE_HEIGHT + 4

    lines = [
        f"Banque: {bank_info.get('bank', '')}",
        f"BIC: {bank_info.get('bic', '')}",
        f"IBAN: {bank_info.get('iban', '')}",
    ]

    for line in lines:
        if line:
            draw.text((MARGIN + 10, y), line, font=normal_font, fill="#333")
            y += LINE_HEIGHT

    return y


def apply_medium_degradation(img):
    """Apply medium quality degradation."""
    # Slight blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Reduce contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.92)

    # Reduce brightness slightly
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.95)

    # Add slight noise
    img = add_noise(img, intensity=8)

    return img


def apply_blur_degradation(img):
    """Apply blur degradation simulating motion/focus issues."""
    # Directional blur (motion effect)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))

    # Reduce contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.85)

    # Add more noise
    img = add_noise(img, intensity=15)

    return img


def apply_poor_degradation(img):
    """Apply poor quality degradation simulating bad phone capture."""
    # Stronger blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Reduce contrast significantly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.75)

    # Add shadows (gradient overlay)
    img = add_shadow_gradient(img)

    # Add significant noise
    img = add_noise(img, intensity=25)

    # Simulate uneven lighting with color cast
    img = add_color_cast(img)

    return img


def add_noise(img, intensity=10):
    """Add Gaussian noise to image."""
    import random
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            noise = random.randint(-intensity, intensity)
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)),
            )

    return img


def add_shadow_gradient(img):
    """Add shadow gradient to simulate uneven lighting."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Add corner shadows
    for i in range(100):
        alpha = int(30 * (1 - i / 100))
        draw.rectangle([i, i, img.width - i, img.height - i], outline=(0, 0, 0, alpha))

    # Add gradient from one corner
    for y in range(img.height):
        for x in range(img.width):
            alpha = int(20 * (1 - x / img.width) * (1 - y / img.height))
            overlay.putpixel((x, y), (0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)

    return img.convert("RGB")


def add_color_cast(img):
    """Add slight color cast to simulate poor white balance."""
    import colorsys

    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][:3]

            # Add slight yellow/blue cast
            r = int(r * 1.02)
            b = int(b * 0.98)

            pixels[x, y] = (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )

    return img


def create_degraded_image(data, quality_type, output_path):
    """Create a degraded version of the invoice image."""
    # First create clean base image in memory
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = get_font(24, bold=True)
    section_font = get_font(16, bold=True)
    normal_font = get_font(14)
    small_font = get_font(12)

    y = MARGIN

    # Render same content as clean image
    invoice_num = data.get("invoice_number", "FACTURE")
    draw.text((MARGIN, y), f"FACTURE N° {invoice_num}", font=title_font, fill="#1a1a1a")
    y += 50

    date_emission = data.get("date_emission", "")
    date_echeance = data.get("date_echeance", "")
    draw.text((MARGIN, y), f"Date d'émission: {date_emission}", font=normal_font, fill="#333")
    y += LINE_HEIGHT
    draw.text((MARGIN, y), f"Date d'échéance: {date_echeance}", font=normal_font, fill="#333")
    y += 40

    y = draw_supplier_section(draw, data.get("supplier", {}), y, section_font, normal_font)
    y += 20
    y = draw_client_section(draw, data.get("client", {}), y, section_font, normal_font)
    y += 40
    y = draw_line_items(draw, data.get("line_items", []), y, section_font, normal_font, small_font)
    y += 40
    y = draw_totals(draw, data.get("totals", {}), y, section_font, normal_font)
    y += 40
    y = draw_bank_info(draw, data.get("bank_info", {}), y, section_font, normal_font)

    draw.text(
        (MARGIN, IMG_HEIGHT - 60),
        "FACTURE EXEMPLE - DOCUMENT NON VALIDE - Généré pour test OCR",
        font=small_font,
        fill="#888"
    )

     # Save based on variant name
    if quality_type == "semi_blur":
        img = apply_blur_degradation(img)
        img.save(output_path, "JPEG", quality=70, dpi=(150, 150))
    elif quality_type == "phone_capture":
        img = apply_poor_degradation(img)  # quick phone-like baseline (you can improve later)
        # More realistic phone capture: rotation + slight perspective
        img = img.rotate(3, resample=Image.BICUBIC, expand=False, fillcolor="white")
        img.save(output_path, "JPEG", quality=60, dpi=(120, 120))
    elif quality_type == "rotation":
        img = apply_medium_degradation(img)
        img = img.rotate(2.5, resample=Image.BICUBIC, expand=False, fillcolor="white")
        img.save(output_path, "JPEG", quality=80, dpi=(200, 200))
    elif quality_type == "low_quality":
        img = apply_poor_degradation(img)
        img.save(output_path, "JPEG", quality=35, dpi=(96, 96))
    else:
        # fallback
        img = apply_medium_degradation(img)
        img.save(output_path, "JPEG", quality=80, dpi=(200, 200))

    return output_path


def generate_manifest(generated_files):
    """Generate a manifest file listing all generated images."""
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.write("# Facture Image Generation Manifest\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total images: {len(generated_files)}\n")
        f.write("\n")
        f.write("# Format: filename | quality_type | quality_level | description | source_file\n")
        f.write("-" * 100 + "\n")

        for entry in generated_files:
            f.write(
                f"{entry['filename']} | {entry['quality_type']} | {entry['quality_level']} | "
                f"{entry['description']} | {entry['source']}\n"
            )

    return MANIFEST_FILE


def main():
    """Main function to generate all facture images."""
    print("=" * 60)
    print("Facture Image Generator - Starting")
    print("=" * 60)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all facture files
    facture_files = sorted(glob.glob(os.path.join(FACTURETXT_DIR, "facture-*.md")))
    print(f"Found {len(facture_files)} facture files in {FACTURETXT_DIR}")

    synthetic_data: List[Dict] = []
    if SYNTHETIC_COUNT > 0:
        print(f"Generating {SYNTHETIC_COUNT} synthetic invoices with Faker...")
        synthetic_data = generate_synthetic_facture_data(SYNTHETIC_COUNT)

    generated_files: List[Dict] = []
    successful = 0
    failed = 0

    def _generate_for_data(data: Dict, source_name: str):
        nonlocal successful, failed

        invoice_num = data.get("invoice_number", "unknown")
        invoice_id = invoice_num.replace("FAC-", "").replace("-", "").zfill(3)
        templates = _resolve_templates()

        if ONE_RANDOM_PER_INVOICE:
            tpl = random.choice(templates)
            quality_type, quality_level, description = random.choice(QUALITY_VARIANTS)
            try:
                base_img = tpl.render_image(data)
                img, params = _apply_quality_variant(base_img, quality_type)
                filename = f"facture_{invoice_id}_{tpl.name}_{quality_type}.jpg"
                output_path = os.path.join(OUTPUT_DIR, filename)
                img.save(output_path, params["format"], quality=params["quality"], dpi=params["dpi"])

                generated_files.append(
                    {
                        "filename": filename,
                        "quality_type": quality_type,
                        "quality_level": quality_level,
                        "description": description,
                        "source": source_name,
                    }
                )
                print(f"  Created: {filename} ({tpl.name}/{quality_type}) [random]")
                successful += 1
            except Exception as e:
                print(f"  Error creating random image for {invoice_id}: {e}")
                failed += 1
            return

        for tpl in templates:
            try:
                base_img = tpl.render_image(data)
            except Exception as e:
                print(f"  Error rendering template {tpl.name}: {e}")
                failed += 1
                continue

            for quality_type, quality_level, description in QUALITY_VARIANTS:
                filename = f"facture_{invoice_id}_{tpl.name}_{quality_type}.jpg"
                output_path = os.path.join(OUTPUT_DIR, filename)
                try:
                    img, params = _apply_quality_variant(base_img, quality_type)
                    img.save(output_path, params["format"], quality=params["quality"], dpi=params["dpi"])

                    generated_files.append(
                        {
                            "filename": filename,
                            "quality_type": quality_type,
                            "quality_level": quality_level,
                            "description": description,
                            "source": source_name,
                        }
                    )
                    print(f"  Created: {filename} ({tpl.name}/{quality_type})")
                    successful += 1
                except Exception as e:
                    print(f"  Error creating {filename}: {e}")
                    failed += 1

    for facture_path in facture_files:
        print(f"\nProcessing: {os.path.basename(facture_path)}")
        data = parse_facture_file(facture_path)
        if "error" in data:
            print(f"  Skipping due to parse error: {data['error']}")
            failed += 1
            continue
        _generate_for_data(data, data.get("source_file", os.path.basename(facture_path)))

    for data in synthetic_data:
        print(f"\nProcessing synthetic: {data.get('invoice_number')}")
        _generate_for_data(data, "synthetic_faker")

    # Generate manifest
    if generated_files:
        manifest_path = generate_manifest(generated_files)
        print(f"\nManifest created: {manifest_path}")

    print("\n" + "=" * 60)
    print(f"Generation complete: {successful} images created, {failed} failed")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

    return generated_files


if __name__ == "__main__":
    main()
