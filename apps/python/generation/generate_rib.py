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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpers"))
from helpers import BANQUES_FR, generate_iban_fr

fake = Faker('fr_FR')
random.seed(11)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "rib", "valides")
os.makedirs(OUTPUT_DIR, exist_ok=True)


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


def build_rib(filename, titulaire, iban_data, banque_nom, banque_bic,
              domiciliation, anomalie_label=None):
    """Construit un PDF de RIB."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles     = getSampleStyleSheet()
    bold       = ParagraphStyle("bold",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal     = ParagraphStyle("normal",  parent=styles["Normal"], fontSize=9)
    small      = ParagraphStyle("small",   parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style= ParagraphStyle("title",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15)
    bank_style = ParagraphStyle("bank",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13,
                                textColor=colors.HexColor("#003366"))
    red_style  = ParagraphStyle("red",     parent=styles["Normal"], fontSize=8,
                                textColor=colors.HexColor("#cc0000"))

    elements = []

    # En-tête : nom de la banque + titre
    elements.append(Paragraph(banque_nom.upper(), bank_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#003366")))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("RELEVÉ D'IDENTITÉ BANCAIRE", title_style))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.5*cm))

    # Titulaire
    elements.append(Paragraph(f"<b>Titulaire du compte :</b> {titulaire['nom']}", bold))
    elements.append(Paragraph(titulaire["adresse"], normal))
    elements.append(Paragraph(titulaire["ville"], normal))
    elements.append(Spacer(1, 0.5*cm))

    # Tableau code banque / guichet / compte / clé
    coord_headers = [
        Paragraph("<b>Code banque</b>", bold),
        Paragraph("<b>Code guichet</b>", bold),
        Paragraph("<b>Numéro de compte</b>", bold),
        Paragraph("<b>Clé RIB</b>", bold),
    ]
    coord_values = [
        Paragraph(iban_data["bank_code"],   normal),
        Paragraph(iban_data["branch_code"], normal),
        Paragraph(iban_data["account"],     normal),
        Paragraph(iban_data["rib_key"],     normal),
    ]
    coord_table = Table([coord_headers, coord_values],
                        colWidths=[3.5*cm, 3.5*cm, 6*cm, 2.5*cm])
    coord_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#003366")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ]))
    elements.append(coord_table)
    elements.append(Spacer(1, 0.5*cm))

    # IBAN et BIC
    iban_table = Table([
        [Paragraph("<b>IBAN</b>", bold), Paragraph(iban_data["iban_formatted"], normal)],
        [Paragraph("<b>BIC / SWIFT</b>", bold), Paragraph(banque_bic, normal)],
    ], colWidths=[4*cm, 13.5*cm])
    iban_table.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LINEBELOW",    (0,0), (-1,0),  0.3, colors.lightgrey),
    ]))
    elements.append(iban_table)
    elements.append(Spacer(1, 0.5*cm))

    # Domiciliation
    elements.append(Paragraph(f"<b>Domiciliation :</b> {domiciliation}", normal))
    elements.append(Spacer(1, 1*cm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Ce document est à conserver. Il vous sera demandé pour tout virement ou prélèvement bancaire.",
        small))

    doc.build(elements)


print("Génération de 30 RIBs valides...")
banque_noms = list(BANQUES_FR.keys())

for i in range(1, 31):
    entreprise  = get_entreprise(df.sample(1).iloc[0])
    iban_data   = generate_iban_fr(fake)
    banque_nom  = random.choice(banque_noms)
    banque_bic  = BANQUES_FR[banque_nom]
    # Domiciliation : agence fictive dans la ville du titulaire
    ville_court = entreprise["ville"].split()[-1] if entreprise["ville"] else fake.city()
    domiciliation = f"{banque_nom} — Agence {ville_court}"

    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"rib_{i:02d}.pdf"),
        titulaire     = entreprise,
        iban_data     = iban_data,
        banque_nom    = banque_nom,
        banque_bic    = banque_bic,
        domiciliation = domiciliation,
    )
    print(f"  ✓ rib_{i:02d}.pdf")

print(f"\nTerminé ! 30 RIBs générés dans {OUTPUT_DIR}/")
