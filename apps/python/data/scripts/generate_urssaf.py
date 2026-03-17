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
from helpers import REGIONS_URSSAF

fake = Faker('fr_FR')
random.seed(55)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "urssaf", "valides")
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
    return {
        "nom":    nom,
        "siret":  row.get("siret", fake.numerify("##############")),
        "adresse": adresse if adresse else fake.street_address(),
        "ville":   ville   if ville   else fake.city(),
    }


def num_cotisant(code_region: str, siret: str) -> str:
    """Génère un numéro de cotisant URSSAF : code région (3) + 9 chiffres + 1 clé."""
    base = siret[:9] if len(siret) >= 9 else fake.numerify("#########")
    cle  = fake.numerify("#")
    return f"{code_region} {base} {cle}"


def build_urssaf(filename, entreprise, region_nom, region_code, num_cot,
                 date_delivrance, date_debut, date_fin, date_validite,
                 code_verif, anomalie_label=None):
    """Construit un PDF d'attestation de vigilance URSSAF."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles      = getSampleStyleSheet()
    bold        = ParagraphStyle("bold",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal      = ParagraphStyle("normal",  parent=styles["Normal"], fontSize=9)
    small       = ParagraphStyle("small",   parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style = ParagraphStyle("title",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14)
    urssaf_blue = ParagraphStyle("blue",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12,
                                 textColor=colors.HexColor("#003189"))
    urssaf_red  = ParagraphStyle("ured",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.HexColor("#E30613"))
    legal_style = ParagraphStyle("legal",   parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#333333"))
    red_style   = ParagraphStyle("red",     parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))
    verif_style = ParagraphStyle("verif",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.HexColor("#003189"))

    elements = []

    # En-tête URSSAF
    elements.append(Paragraph(f"URSSAF {region_nom}", urssaf_blue))
    elements.append(Paragraph(f"Code région : {region_code}", urssaf_red))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=2,
                               color=colors.HexColor("#E30613")))
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph("ATTESTATION DE VIGILANCE", title_style))
    elements.append(Paragraph(
        "Délivrée en application de l'article L.243-15 du Code de la Sécurité Sociale",
        small))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.6*cm))

    # Identification cotisant
    elements.append(Paragraph("IDENTIFICATION DU COTISANT", bold))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5,
                               color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))

    champs_id = [
        ["Numéro de cotisant :", num_cot if num_cot else ""],
        ["Raison sociale :",     entreprise["nom"]],
        ["SIRET :",              entreprise["siret"]],
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

    # Période et validité
    elements.append(Paragraph("PÉRIODE ET VALIDITÉ", bold))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5,
                               color=colors.HexColor("#003189")))
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

    # Déclaration légale + code de vérification
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


print("Génération de 30 attestations URSSAF valides...")
regions = list(REGIONS_URSSAF.items())

for i in range(1, 31):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    region_nom, region_code = random.choice(regions)
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    # Période : trimestre précédent
    date_debut      = fake.date_between(start_date="-6m", end_date="-3m")
    date_fin        = date_debut + timedelta(days=90)
    date_validite   = date_delivrance + timedelta(days=180)   # +6 mois légal
    num_cot         = num_cotisant(region_code, entreprise["siret"])
    code_verif      = fake.numerify("########").upper()

    build_urssaf(
        filename        = os.path.join(OUTPUT_DIR, f"urssaf_{i:02d}.pdf"),
        entreprise      = entreprise,
        region_nom      = region_nom,
        region_code     = region_code,
        num_cot         = num_cot,
        date_delivrance = date_delivrance,
        date_debut      = date_debut,
        date_fin        = date_fin,
        date_validite   = date_validite,
        code_verif      = code_verif,
    )
    print(f"  ✓ urssaf_{i:02d}.pdf")

print(f"\nTerminé ! 30 attestations URSSAF générées dans {OUTPUT_DIR}/")
