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
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import FORMES_JURIDIQUES, CODES_NAF_LIBELLES

fake = Faker('fr_FR')
random.seed(33)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "siret", "valides")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_entreprise(row):
    nom = row.get("denominationUniteLegale", "").strip()
    if not nom:
        nom = f"{row.get('nomUniteLegale','')} {row.get('prénomUsuelUniteLegale','')}".strip()
    if not nom:
        nom = fake.company()
    adresse = f"{row.get('numeroVoieEtablissement','')} {row.get('typeVoieEtablissement','')} {row.get('libelleVoieEtablissement','')}".strip()
    ville   = f"{row.get('codePostalEtablissement','')} {row.get('libelleCommuneEtablissement','')}".strip()
    naf_csv = row.get("activitePrincipaleEtablissement", "").strip()
    naf     = naf_csv if naf_csv else random.choice(list(CODES_NAF_LIBELLES.keys()))
    return {
        "nom":    nom,
        "siret":  row.get("siret", fake.numerify("##############")),
        "siren":  row.get("siren",  fake.numerify("#########")),
        "adresse": adresse if adresse else fake.street_address(),
        "ville":   ville   if ville   else fake.city(),
        "naf":     naf,
        "naf_libelle": CODES_NAF_LIBELLES.get(naf, "Activité non renseignée"),
        "etat":   row.get("etatAdministratifEtablissement", "A"),
        "forme":  random.choice(FORMES_JURIDIQUES),
        "date_creation": fake.date_between(start_date="-20y", end_date="-1y").strftime("%d/%m/%Y"),
    }


def build_siret(filename, entreprise, date_delivrance, anomalie_label=None):
    """Construit un PDF d'attestation SIRET (style INSEE)."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles      = getSampleStyleSheet()
    bold        = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal      = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    small       = ParagraphStyle("small",  parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style = ParagraphStyle("title",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14)
    insee_style = ParagraphStyle("insee",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11,
                                 textColor=colors.HexColor("#003189"))
    red_style   = ParagraphStyle("red",    parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))
    actif_style = ParagraphStyle("actif",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
                                 textColor=colors.HexColor("#1a7a1a"))

    elements = []

    # En-tête INSEE
    elements.append(Paragraph("INSEE — Institut National de la Statistique", insee_style))
    elements.append(Paragraph("et des Études Économiques", insee_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph("AVIS DE SITUATION AU RÉPERTOIRE SIRENE", title_style))
    elements.append(Paragraph(f"Délivré le : {date_delivrance.strftime('%d/%m/%Y')}", normal))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.6*cm))

    # Bloc identification
    elements.append(Paragraph("IDENTIFICATION DE L'ÉTABLISSEMENT", bold))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))

    champs = [
        ["Dénomination :", entreprise["nom"]],
        ["Forme juridique :", entreprise["forme"]],
        ["SIREN :", entreprise["siren"]],
        ["SIRET :", entreprise["siret"]],
        ["Code APE / NAF :", f"{entreprise['naf']} — {entreprise['naf_libelle']}"],
        ["Date de création :", entreprise["date_creation"]],
        ["Adresse :", entreprise["adresse"]],
        ["Commune :", entreprise["ville"]],
    ]

    for label, valeur in champs:
        row_table = Table(
            [[Paragraph(f"<b>{label}</b>", bold), Paragraph(valeur, normal)]],
            colWidths=[5*cm, 12.5*cm]
        )
        row_table.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LINEBELOW",    (0,0), (-1,-1), 0.2, colors.HexColor("#dddddd")),
        ]))
        elements.append(row_table)

    elements.append(Spacer(1, 0.5*cm))

    # État administratif
    etat_libelle = "ACTIF" if entreprise["etat"] == "A" else "FERMÉ"
    etat_color   = colors.HexColor("#1a7a1a") if entreprise["etat"] == "A" else colors.HexColor("#cc0000")
    etat_style   = ParagraphStyle("etat", parent=styles["Normal"], fontName="Helvetica-Bold",
                                  fontSize=11, textColor=etat_color)
    elements.append(Paragraph("ÉTAT DE L'ÉTABLISSEMENT", bold))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"● {etat_libelle}", etat_style))
    elements.append(Spacer(1, 0.8*cm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Ce document est un avis de situation délivré par le répertoire Sirene de l'INSEE. "
        "Il ne constitue pas un extrait Kbis et n'a pas de valeur juridique en tant que tel.",
        small))

    doc.build(elements)


print("Génération de 30 attestations SIRET valides...")
for i in range(1, 31):
    entreprise     = get_entreprise(df.sample(1).iloc[0])
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")

    build_siret(
        filename       = os.path.join(OUTPUT_DIR, f"siret_{i:02d}.pdf"),
        entreprise     = entreprise,
        date_delivrance= date_delivrance,
    )
    print(f"  ✓ siret_{i:02d}.pdf")

print(f"\nTerminé ! 30 attestations SIRET générées dans {OUTPUT_DIR}/")
