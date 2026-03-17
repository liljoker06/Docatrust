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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpers"))
from helpers import FORMES_JURIDIQUES, CODES_NAF_LIBELLES, corrupt_siret

fake = Faker('fr_FR')
random.seed(44)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "siret", "erronees")
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


def build_siret(filename, entreprise, date_delivrance, anomalie_label=None,
                siret_override=None, naf_override=None, etat_override=None, nom_override=None):
    """Construction PDF attestation SIRET — paramètres overridables pour les cas erronés."""
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

    siret_affiche = siret_override if siret_override is not None else entreprise["siret"]
    naf_affiche   = naf_override   if naf_override   is not None else f"{entreprise['naf']} — {entreprise['naf_libelle']}"
    etat_affiche  = etat_override  if etat_override  is not None else entreprise["etat"]
    nom_affiche   = nom_override   if nom_override   is not None else entreprise["nom"]

    elements = []

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

    elements.append(Paragraph("IDENTIFICATION DE L'ÉTABLISSEMENT", bold))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#003189")))
    elements.append(Spacer(1, 0.3*cm))

    champs = [
        ["Dénomination :", nom_affiche],
        ["Forme juridique :", entreprise["forme"]],
        ["SIREN :", entreprise["siren"]],
        ["SIRET :", siret_affiche],
        ["Code APE / NAF :", naf_affiche],
        ["Date de création :", entreprise["date_creation"]],
        ["Adresse :", entreprise["adresse"]],
        ["Commune :", entreprise["ville"]],
    ]

    for label, valeur in champs:
        row_t = Table(
            [[Paragraph(f"<b>{label}</b>", bold), Paragraph(str(valeur), normal)]],
            colWidths=[5*cm, 12.5*cm]
        )
        row_t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LINEBELOW",    (0,0), (-1,-1), 0.2, colors.HexColor("#dddddd")),
        ]))
        elements.append(row_t)

    elements.append(Spacer(1, 0.5*cm))

    etat_libelle = "ACTIF" if etat_affiche == "A" else "FERMÉ"
    etat_color   = colors.HexColor("#1a7a1a") if etat_affiche == "A" else colors.HexColor("#cc0000")
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


# ─────────────────────────────────────────────
# CAS 1 — SIRET INVALIDE (clé de contrôle Luhn erronée)
# Le dernier chiffre du SIRET est altéré
# ─────────────────────────────────────────────
print("Génération cas 1 : SIRET invalide (Luhn faux)...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    siret_faux      = corrupt_siret(entreprise["siret"])

    build_siret(
        filename      = os.path.join(OUTPUT_DIR, f"cas1_siret_invalide_{i:02d}.pdf"),
        entreprise    = entreprise,
        date_delivrance = date_delivrance,
        siret_override= siret_faux,
        anomalie_label= "SIRET INVALIDE (LUHN FAUX)",
    )
    print(f"  ✓ cas1_siret_invalide_{i:02d}.pdf")
print("Done ! Cas 1 terminé.\n")


# ─────────────────────────────────────────────
# CAS 2 — SIRET ≠ NOM D'ENTREPRISE
# Le SIRET appartient à une entreprise, le nom affiché à une autre
# ─────────────────────────────────────────────
print("Génération cas 2 : SIRET ≠ nom d'entreprise...")
for i in range(1, 11):
    entreprise_siret = get_entreprise(df.sample(1).iloc[0])
    entreprise_nom   = get_entreprise(df.sample(1).iloc[0])
    while entreprise_nom["siret"] == entreprise_siret["siret"]:
        entreprise_nom = get_entreprise(df.sample(1).iloc[0])
    date_delivrance  = fake.date_between(start_date="-3m", end_date="today")

    build_siret(
        filename      = os.path.join(OUTPUT_DIR, f"cas2_siret_nom_incoherent_{i:02d}.pdf"),
        entreprise    = entreprise_siret,
        date_delivrance = date_delivrance,
        nom_override  = entreprise_nom["nom"],      # ← nom d'une autre société
        anomalie_label= "SIRET ≠ NOM ENTREPRISE",
    )
    print(f"  ✓ cas2_siret_nom_incoherent_{i:02d}.pdf")
print("Done ! Cas 2 terminé.\n")


# ─────────────────────────────────────────────
# CAS 3 — ATTESTATION EXPIRÉE
# Date de délivrance ancienne (> 3 mois — périmée légalement)
# ─────────────────────────────────────────────
print("Génération cas 3 : attestation expirée...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    # Date de délivrance entre 6 mois et 3 ans dans le passé
    date_delivrance = fake.date_between(start_date="-3y", end_date="-6m")

    build_siret(
        filename      = os.path.join(OUTPUT_DIR, f"cas3_attestation_expiree_{i:02d}.pdf"),
        entreprise    = entreprise,
        date_delivrance = date_delivrance,
        anomalie_label= "ATTESTATION EXPIRÉE (> 3 MOIS)",
    )
    print(f"  ✓ cas3_attestation_expiree_{i:02d}.pdf")
print("Done ! Cas 3 terminé.\n")


# ─────────────────────────────────────────────
# CAS 4 — CODE NAF MANQUANT
# Le champ code APE/NAF est absent
# ─────────────────────────────────────────────
print("Génération cas 4 : code NAF manquant...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")

    build_siret(
        filename      = os.path.join(OUTPUT_DIR, f"cas4_naf_manquant_{i:02d}.pdf"),
        entreprise    = entreprise,
        date_delivrance = date_delivrance,
        naf_override  = "",                         # ← champ vide
        anomalie_label= "CODE NAF MANQUANT",
    )
    print(f"  ✓ cas4_naf_manquant_{i:02d}.pdf")
print("Done ! Cas 4 terminé.\n")


# ─────────────────────────────────────────────
# CAS 5 — ÉTAT ADMINISTRATIF INCOHÉRENT
# L'attestation indique ACTIF mais la société est présentée comme fermée
# ─────────────────────────────────────────────
print("Génération cas 5 : état administratif incohérent...")
for i in range(1, 11):
    entreprise      = get_entreprise(df.sample(1).iloc[0])
    date_delivrance = fake.date_between(start_date="-3m", end_date="today")
    # Force l'état à fermé alors que le reste du document laisse penser actif
    build_siret(
        filename      = os.path.join(OUTPUT_DIR, f"cas5_etat_incoherent_{i:02d}.pdf"),
        entreprise    = entreprise,
        date_delivrance = date_delivrance,
        etat_override = "F",                        # ← FERMÉ alors que dossier actif
        anomalie_label= "ÉTAT ADMINISTRATIF INCOHÉRENT",
    )
    print(f"  ✓ cas5_etat_incoherent_{i:02d}.pdf")
print("Done ! Cas 5 terminé.\n")

print(f"Terminé ! 50 attestations SIRET erronées générées dans {OUTPUT_DIR}/")
