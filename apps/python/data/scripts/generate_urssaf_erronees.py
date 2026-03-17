import pandas as pd
import random
import sys
import os
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import REGIONS_URSSAF, corrupt_siret

fake = Faker('fr_FR')
random.seed(66)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "urssaf", "erronees")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEXTE_LEGAL = (
    "En application de l'article L.243-15 du Code de la Sécurité Sociale, "
    "l'employeur susmentionné est à jour de ses obligations déclaratives et de paiement "
    "à l'égard de l'URSSAF à la date de délivrance du présent document. "
    "Ce document ne vaut que pour la période indiquée."
)


def get_entreprise(row):
    nom = row.get("denominationUniteLegale", "").strip()
    if not nom:
        nom = f"{row.get('nomUniteLegale','')} {row.get('prénomUsuelUniteLegale','')}".strip()
    if not nom:
        nom = fake.company()
    adresse = f"{row.get('numeroVoieEtablissement','')} {row.get('typeVoieEtablissement','')} {row.get('libelleVoieEtablissement','')}".strip()
    ville   = f"{row.get('codePostalEtablissement','')} {row.get('libelleCommuneEtablissement','')}".strip()
    code_postal = row.get("codePostalEtablissement", "").strip()
    return {
        "nom":         nom,
        "siret":       row.get("siret", fake.numerify("##############")),
        "adresse":     adresse if adresse else fake.street_address(),
        "ville":       ville   if ville   else fake.city(),
        "code_postal": code_postal,
    }


def num_cotisant(code_region: str, siret: str) -> str:
    base = siret[:9] if len(siret) >= 9 else fake.numerify("#########")
    return f"{code_region} {base} {fake.numerify('#')}"


def build_urssaf(filename, entreprise, region_nom, region_code, num_cot,
                 date_delivrance, date_debut, date_fin, date_validite,
                 code_verif, anomalie_label=None, siret_override=None):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles      = getSampleStyleSheet()
    bold        = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal      = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    small       = ParagraphStyle("small",  parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style = ParagraphStyle("title",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14)
    urssaf_blue = ParagraphStyle("blue",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12,
                                 textColor=colors.HexColor("#003189"))
    urssaf_red  = ParagraphStyle("ured",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.HexColor("#E30613"))
    legal_style = ParagraphStyle("legal",  parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#333333"))
    red_style   = ParagraphStyle("red",    parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))
    verif_style = ParagraphStyle("verif",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.HexColor("#003189"))

    siret_affiche = siret_override if siret_override is not None else entreprise["siret"]

    elements = []

    elements.append(Paragraph(f"URSSAF {region_nom}", urssaf_blue))
    elements.append(Paragraph(f"Code région : {region_code}", urssaf_red))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#E30613")))
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph("ATTESTATION DE VIGILANCE", title_style))
    elements.append(Paragraph(
        "Délivrée en application de l'article L.243-15 du Code de la Sécurité Sociale", small))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.6*cm))

    elements.append(Paragraph("IDENTIFICATION DU COTISANT", bold))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))

    champs_id = [
        ["Numéro de cotisant :", num_cot if num_cot else ""],
        ["Raison sociale :",     entreprise["nom"]],
        ["SIRET :",              siret_affiche],
        ["Adresse :",            entreprise["adresse"]],
        ["Commune :",            entreprise["ville"]],
    ]
    for label, valeur in champs_id:
        t = Table([[Paragraph(f"<b>{label}</b>", bold), Paragraph(str(valeur), normal)]],
                  colWidths=[5*cm, 12.5*cm])
        t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LINEBELOW",    (0,0), (-1,-1), 0.2, colors.HexColor("#dddddd")),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("PÉRIODE ET VALIDITÉ", bold))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))

    champs_periode = [
        ["Période couverte :",
         f"du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"],
        ["Date de délivrance :", date_delivrance.strftime('%d/%m/%Y')],
        ["Valable jusqu'au :",   date_validite.strftime('%d/%m/%Y')],
    ]
    for label, valeur in champs_periode:
        t = Table([[Paragraph(f"<b>{label}</b>", bold), Paragraph(valeur, normal)]],
                  colWidths=[5*cm, 12.5*cm])
        t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LINEBELOW",    (0,0), (-1,-1), 0.2, colors.HexColor("#dddddd")),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 0.6*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(TEXTE_LEGAL, legal_style))
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph(f"Code de vérification : {code_verif}", verif_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Ce document peut être vérifié sur net-entreprises.fr avec le code de vérification ci-dessus.",
        small))

    doc.build(elements)


regions = list(REGIONS_URSSAF.items())


# ─────────────────────────────────────────────
# CAS 1 — ATTESTATION EXPIRÉE (> 6 mois)
# La date de délivrance est ancienne, la validité est passée
# ─────────────────────────────────────────────
print("Génération cas 1 : attestation expirée (> 6 mois)...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    region_nom, region_code = random.choice(regions)
    # Délivrance entre 2 et 3 ans dans le passé → expirée depuis longtemps
    date_delivrance = fake.date_between(start_date="-3y", end_date="-2y")
    date_debut      = date_delivrance - timedelta(days=90)
    date_fin        = date_delivrance - timedelta(days=1)
    date_validite   = date_delivrance + timedelta(days=180)   # même passée

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"cas1_attestation_expiree_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,
        num_cot         = num_cotisant(region_code, entreprise["siret"]),
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,
        date_validite   = date_validite,
        code_verif      = fake.numerify("########"),
        anomalie_label  = "ATTESTATION EXPIRÉE (> 6 MOIS)",
    )
    print(f"  ✓ cas1_attestation_expiree_{i:02d}.pdf")
print("Done ! Cas 1 terminé.\n")


# ─────────────────────────────────────────────
# CAS 2 — SIRET INVALIDE (Luhn faux)
# Le SIRET dans l'attestation ne passe pas le contrôle de clé
# ─────────────────────────────────────────────
print("Génération cas 2 : SIRET invalide (Luhn faux)...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    region_nom, region_code = random.choice(regions)
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    date_debut      = fake.date_between(start_date="-6m", end_date="-3m")
    date_fin        = date_debut + timedelta(days=90)
    date_validite   = date_delivrance + timedelta(days=180)
    siret_faux      = corrupt_siret(entreprise["siret"])

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"cas2_siret_invalide_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,
        num_cot         = num_cotisant(region_code, entreprise["siret"]),
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,
        date_validite   = date_validite,
        code_verif      = fake.numerify("########"),
        siret_override  = siret_faux,
        anomalie_label  = "SIRET INVALIDE (LUHN FAUX)",
    )
    print(f"  ✓ cas2_siret_invalide_{i:02d}.pdf")
print("Done ! Cas 2 terminé.\n")


# ─────────────────────────────────────────────
# CAS 3 — NUMÉRO DE COTISANT MANQUANT
# Le champ numéro de cotisant est absent
# ─────────────────────────────────────────────
print("Génération cas 3 : numéro de cotisant manquant...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    region_nom, region_code = random.choice(regions)
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    date_debut      = fake.date_between(start_date="-6m", end_date="-3m")
    date_fin        = date_debut + timedelta(days=90)
    date_validite   = date_delivrance + timedelta(days=180)

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"cas3_num_cotisant_manquant_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,
        num_cot         = None,            # ← absent volontairement
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,
        date_validite   = date_validite,
        code_verif      = fake.numerify("########"),
        anomalie_label  = "NUMÉRO COTISANT MANQUANT",
    )
    print(f"  ✓ cas3_num_cotisant_manquant_{i:02d}.pdf")
print("Done ! Cas 3 terminé.\n")


# ─────────────────────────────────────────────
# CAS 4 — PÉRIODE INCOHÉRENTE (fin < début)
# La date de fin de période est antérieure à la date de début
# ─────────────────────────────────────────────
print("Génération cas 4 : période incohérente (fin < début)...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    region_nom, region_code = random.choice(regions)
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    date_debut      = fake.date_between(start_date="-3m", end_date="today")
    # Fin antérieure au début → incohérent
    date_fin        = date_debut - timedelta(days=random.randint(1, 60))
    date_validite   = date_delivrance + timedelta(days=180)

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"cas4_periode_incoherente_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,
        num_cot         = num_cotisant(region_code, entreprise["siret"]),
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,          # ← fin < début
        date_validite   = date_validite,
        code_verif      = fake.numerify("########"),
        anomalie_label  = "PÉRIODE INCOHÉRENTE (FIN < DÉBUT)",
    )
    print(f"  ✓ cas4_periode_incoherente_{i:02d}.pdf")
print("Done ! Cas 4 terminé.\n")


# ─────────────────────────────────────────────
# CAS 5 — RÉGION URSSAF INCOHÉRENTE AVEC L'ADRESSE
# Le code région URSSAF ne correspond pas au département de l'entreprise
# ─────────────────────────────────────────────
print("Génération cas 5 : région URSSAF incohérente avec l'adresse...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    date_debut      = fake.date_between(start_date="-6m", end_date="-3m")
    date_fin        = date_debut + timedelta(days=90)
    date_validite   = date_delivrance + timedelta(days=180)

    # Département réel de l'entreprise (2 premiers chiffres du CP)
    dept = entreprise["code_postal"][:2] if len(entreprise["code_postal"]) >= 2 else "75"

    # Région dont le code NE correspond PAS au département
    region_incoherente = random.choice([
        (r, c) for r, c in regions if c[:2] != dept
    ])
    region_nom, region_code = region_incoherente

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"cas5_region_incoherente_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,      # ← région ≠ département adresse
        num_cot         = num_cotisant(region_code, entreprise["siret"]),
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,
        date_validite   = date_validite,
        code_verif      = fake.numerify("########"),
        anomalie_label  = f"RÉGION INCOHÉRENTE ({region_code} ≠ dept {dept})",
    )
    print(f"  ✓ cas5_region_incoherente_{i:02d}.pdf")
print("Done ! Cas 5 terminé.\n")

print(f"Terminé ! 50 attestations URSSAF erronées générées dans {OUTPUT_DIR}/")
