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
from helpers import FORMES_JURIDIQUES, CODES_NAF_LIBELLES, TRIBUNAUX_COMMERCE, FONCTIONS_DIRIGEANT

fake = Faker('fr_FR')
random.seed(77)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "kbis", "valides")
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
        "forme":  random.choice(FORMES_JURIDIQUES),
    }


def gen_dirigeant():
    return {
        "nom":        fake.last_name().upper(),
        "prenom":     fake.first_name(),
        "naissance":  fake.date_of_birth(minimum_age=30, maximum_age=70).strftime("%d/%m/%Y"),
        "nationalite": "Française",
        "adresse":    fake.street_address(),
        "ville":      f"{fake.postcode()} {fake.city()}",
        "fonction":   random.choice(FONCTIONS_DIRIGEANT),
    }


def section_header(text, bold_style):
    return Paragraph(text, bold_style)


def champ_row(label, valeur, bold, normal):
    t = Table(
        [[Paragraph(f"<b>{label}</b>", bold), Paragraph(str(valeur), normal)]],
        colWidths=[6*cm, 11.5*cm]
    )
    t.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LINEBELOW",    (0,0), (-1,-1), 0.2, colors.HexColor("#dddddd")),
    ]))
    return t


def build_kbis(filename, entreprise, dirigeant, tribunal, date_immat,
               date_delivrance, capital, objet_social,
               anomalie_label=None, siren_override=None,
               capital_override=None, dirigeant_override=None):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles      = getSampleStyleSheet()
    bold        = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal      = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    small       = ParagraphStyle("small",  parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style = ParagraphStyle("title",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15)
    greffe_style= ParagraphStyle("greffe", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11,
                                 textColor=colors.HexColor("#1a3a5c"))
    sec_style   = ParagraphStyle("sec",    parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.HexColor("#1a3a5c"))
    red_style   = ParagraphStyle("red",    parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))

    siren_affiche   = siren_override   if siren_override   is not None else entreprise["siren"]
    capital_affiche = capital_override if capital_override is not None else f"{capital:,.0f} €".replace(",", " ")
    dir_affiche     = dirigeant_override if dirigeant_override is not None else dirigeant

    rcs = f"RCS {tribunal} {siren_affiche}"
    elements = []

    # ── En-tête greffe
    elements.append(Paragraph(f"GREFFE DU TRIBUNAL DE COMMERCE DE {tribunal.upper()}", greffe_style))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("EXTRAIT KBIS", title_style))
    elements.append(Paragraph(
        f"Délivré le : {date_delivrance.strftime('%d/%m/%Y')}  |  N° RCS : {rcs}", normal))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.5*cm))

    # ── Section 1 : Identification
    elements.append(section_header("1 — IDENTIFICATION DE LA SOCIÉTÉ", sec_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a3a5c")))
    elements.append(Spacer(1, 0.2*cm))
    for label, val in [
        ("Dénomination :",      entreprise["nom"]),
        ("Forme juridique :",   entreprise["forme"]),
        ("Capital social :",    capital_affiche),
        ("SIREN :",             siren_affiche),
        ("SIRET (siège) :",     entreprise["siret"]),
        ("Date d'immatriculation :", date_immat.strftime("%d/%m/%Y")),
    ]:
        elements.append(champ_row(label, val, bold, normal))
    elements.append(Spacer(1, 0.4*cm))

    # ── Section 2 : Siège social
    elements.append(section_header("2 — SIÈGE SOCIAL", sec_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a3a5c")))
    elements.append(Spacer(1, 0.2*cm))
    for label, val in [
        ("Adresse :", entreprise["adresse"]),
        ("Commune :", entreprise["ville"]),
    ]:
        elements.append(champ_row(label, val, bold, normal))
    elements.append(Spacer(1, 0.4*cm))

    # ── Section 3 : Activité
    elements.append(section_header("3 — ACTIVITÉ", sec_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a3a5c")))
    elements.append(Spacer(1, 0.2*cm))
    for label, val in [
        ("Code APE / NAF :", f"{entreprise['naf']} — {entreprise['naf_libelle']}"),
        ("Objet social :",   objet_social),
    ]:
        elements.append(champ_row(label, val, bold, normal))
    elements.append(Spacer(1, 0.4*cm))

    # ── Section 4 : Dirigeants
    elements.append(section_header("4 — DIRIGEANTS", sec_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a3a5c")))
    elements.append(Spacer(1, 0.2*cm))
    if dir_affiche:
        for label, val in [
            ("Fonction :",          dir_affiche["fonction"]),
            ("Nom :",               f"{dir_affiche['nom']} {dir_affiche['prenom']}"),
            ("Date de naissance :", dir_affiche["naissance"]),
            ("Nationalité :",       dir_affiche["nationalite"]),
            ("Adresse :",           dir_affiche["adresse"]),
            ("Commune :",           dir_affiche["ville"]),
        ]:
            elements.append(champ_row(label, val, bold, normal))
    elements.append(Spacer(1, 0.6*cm))

    # ── Pied de page
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Cet extrait Kbis est délivré par le greffe du tribunal de commerce. "
        "Il constitue la « carte d'identité » de l'entreprise et atteste de son existence légale. "
        "Sa durée de validité est de 3 mois à compter de la date de délivrance.",
        small))

    doc.build(elements)


print("Génération de 30 extraits Kbis valides...")
for i in range(1, 31):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    dirigeant       = gen_dirigeant()
    tribunal        = random.choice(TRIBUNAUX_COMMERCE)
    date_immat      = fake.date_between(start_date="-20y", end_date="-1y")
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    capital         = random.choice([1000, 5000, 10000, 50000, 100000, 250000, 500000])
    objet_social    = fake.bs().capitalize() + ". " + fake.catch_phrase() + "."

    build_kbis(
        filename        = os.path.join(OUTPUT_DIR, f"kbis_{i:02d}.pdf"),
        entreprise      = entreprise,
        dirigeant       = dirigeant,
        tribunal        = tribunal,
        date_immat      = date_immat,
        date_delivrance = date_delivrance,
        capital         = capital,
        objet_social    = objet_social,
    )
    print(f"  ✓ kbis_{i:02d}.pdf")

print(f"\nTerminé ! 30 extraits Kbis générés dans {OUTPUT_DIR}/")
