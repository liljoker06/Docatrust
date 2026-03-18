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
from helpers import BANQUES_FR, generate_iban_fr, corrupt_iban_checksum, format_iban

fake = Faker('fr_FR')
random.seed(22)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "rib", "erronees")
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


def build_rib(filename, titulaire, iban_str, iban_formatted, banque_nom, banque_bic,
              domiciliation, bank_code, branch_code, account, rib_key,
              anomalie_label=None):
    """Construction PDF RIB — paramètres déconstruits pour permettre les altérations."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles      = getSampleStyleSheet()
    bold        = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal      = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    small       = ParagraphStyle("small",  parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    title_style = ParagraphStyle("title",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15)
    bank_style  = ParagraphStyle("bank",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13,
                                 textColor=colors.HexColor("#003366"))
    red_style   = ParagraphStyle("red",    parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))

    elements = []

    elements.append(Paragraph(banque_nom.upper(), bank_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#003366")))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("RELEVÉ D'IDENTITÉ BANCAIRE", title_style))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph(f"<b>Titulaire du compte :</b> {titulaire['nom']}", bold))
    elements.append(Paragraph(titulaire["adresse"], normal))
    elements.append(Paragraph(titulaire["ville"], normal))
    elements.append(Spacer(1, 0.5*cm))

    coord_table = Table(
        [[Paragraph("<b>Code banque</b>", bold), Paragraph("<b>Code guichet</b>", bold),
          Paragraph("<b>Numéro de compte</b>", bold), Paragraph("<b>Clé RIB</b>", bold)],
         [Paragraph(bank_code, normal), Paragraph(branch_code, normal),
          Paragraph(account, normal),   Paragraph(rib_key, normal)]],
        colWidths=[3.5*cm, 3.5*cm, 6*cm, 2.5*cm]
    )
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

    iban_table = Table([
        [Paragraph("<b>IBAN</b>", bold), Paragraph(iban_formatted if iban_formatted else "", normal)],
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

    elements.append(Paragraph(f"<b>Domiciliation :</b> {domiciliation}", normal))
    elements.append(Spacer(1, 1*cm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Ce document est à conserver. Il vous sera demandé pour tout virement ou prélèvement bancaire.",
        small))

    doc.build(elements)


banque_noms = list(BANQUES_FR.keys())


# ─────────────────────────────────────────────
# CAS 1 — IBAN INVALIDE (checksum faux)
# Les 2 chiffres de contrôle de l'IBAN sont délibérément erronés
# ─────────────────────────────────────────────
print("Génération cas 1 : IBAN invalide (checksum faux)...")
for i in range(1, 11):
    entreprise    = get_entreprise(df.sample(1).iloc[0])
    iban_data     = generate_iban_fr(fake)
    iban_corrompu = corrupt_iban_checksum(iban_data["iban"])
    banque_nom    = random.choice(banque_noms)
    banque_bic    = BANQUES_FR[banque_nom]
    ville_court   = entreprise["ville"].split()[-1] if entreprise["ville"] else fake.city()

    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"cas1_iban_invalide_{i:02d}.pdf"),
        titulaire     = entreprise,
        iban_str      = iban_corrompu,
        iban_formatted= format_iban(iban_corrompu),   # check digits faux mais IBAN affiché
        banque_nom    = banque_nom,
        banque_bic    = banque_bic,
        domiciliation = f"{banque_nom} — Agence {ville_court}",
        bank_code     = iban_data["bank_code"],
        branch_code   = iban_data["branch_code"],
        account       = iban_data["account"],
        rib_key       = iban_data["rib_key"],
        anomalie_label= "IBAN INVALIDE (CHECKSUM FAUX)",
    )
    print(f"  ✓ cas1_iban_invalide_{i:02d}.pdf")
print("Done ! Cas 1 terminé.\n")


# ─────────────────────────────────────────────
# CAS 2 — BIC INCOHÉRENT
# Le BIC affiché ne correspond pas à la banque nommée
# ─────────────────────────────────────────────
print("Génération cas 2 : BIC incohérent avec la banque...")
for i in range(1, 11):
    entreprise  = get_entreprise(df.sample(1).iloc[0])
    iban_data   = generate_iban_fr(fake)
    banque_nom  = random.choice(banque_noms)
    banque_bic_correct = BANQUES_FR[banque_nom]
    # BIC d'une autre banque (forcément différent)
    autre_banque = random.choice([b for b in banque_noms if b != banque_nom])
    bic_faux     = BANQUES_FR[autre_banque]
    ville_court  = entreprise["ville"].split()[-1] if entreprise["ville"] else fake.city()

    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"cas2_bic_incoherent_{i:02d}.pdf"),
        titulaire     = entreprise,
        iban_str      = iban_data["iban"],
        iban_formatted= iban_data["iban_formatted"],
        banque_nom    = banque_nom,
        banque_bic    = bic_faux,              # ← BIC d'une autre banque
        domiciliation = f"{banque_nom} — Agence {ville_court}",
        bank_code     = iban_data["bank_code"],
        branch_code   = iban_data["branch_code"],
        account       = iban_data["account"],
        rib_key       = iban_data["rib_key"],
        anomalie_label= "BIC INCOHÉRENT",
    )
    print(f"  ✓ cas2_bic_incoherent_{i:02d}.pdf")
print("Done ! Cas 2 terminé.\n")


# ─────────────────────────────────────────────
# CAS 3 — TITULAIRE DIFFÉRENT DU SIRET
# Le nom du titulaire sur le RIB ne correspond pas à l'entreprise du dossier
# ─────────────────────────────────────────────
print("Génération cas 3 : titulaire différent du SIRET...")
for i in range(1, 11):
    # Deux entreprises différentes : une pour le SIRET, une autre pour le titulaire
    entreprise_siret    = get_entreprise(df.sample(1).iloc[0])
    entreprise_titulaire = get_entreprise(df.sample(1).iloc[0])
    # S'assurer que ce ne soit pas accidentellement la même
    while entreprise_titulaire["siret"] == entreprise_siret["siret"]:
        entreprise_titulaire = get_entreprise(df.sample(1).iloc[0])

    iban_data  = generate_iban_fr(fake)
    banque_nom = random.choice(banque_noms)
    banque_bic = BANQUES_FR[banque_nom]
    ville_court= entreprise_titulaire["ville"].split()[-1] if entreprise_titulaire["ville"] else fake.city()

    # Le RIB affiche le titulaire ≠ SIRET
    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"cas3_titulaire_different_{i:02d}.pdf"),
        titulaire     = entreprise_titulaire,   # ← titulaire incohérent
        iban_str      = iban_data["iban"],
        iban_formatted= iban_data["iban_formatted"],
        banque_nom    = banque_nom,
        banque_bic    = banque_bic,
        domiciliation = f"{banque_nom} — Agence {ville_court}",
        bank_code     = iban_data["bank_code"],
        branch_code   = iban_data["branch_code"],
        account       = iban_data["account"],
        rib_key       = iban_data["rib_key"],
        anomalie_label= f"TITULAIRE ≠ SIRET ({entreprise_siret['siret']})",
    )
    print(f"  ✓ cas3_titulaire_different_{i:02d}.pdf")
print("Done ! Cas 3 terminé.\n")


# ─────────────────────────────────────────────
# CAS 4 — DOMICILIATION BANCAIRE ÉTRANGÈRE
# L'IBAN est dans un pays étranger pour une entreprise française
# ─────────────────────────────────────────────
IBANS_ETRANGERS = [
    ("DE", "DE89370400440532013000", "DE89 3704 0044 0532 0130 00", "COBADEFFXXX", "Commerzbank"),
    ("GB", "GB29NWBK60161331926819", "GB29 NWBK 6016 1331 9268 19", "NWBKGB2L", "NatWest"),
    ("ES", "ES9121000418450200051332","ES91 2100 0418 4502 0005 1332","CAIXESBBXXX","CaixaBank"),
    ("IT", "IT60X0542811101000000123456","IT60 X054 2811 1010 0000 0123 456","BLOPIT22XXX","Banca d'Italia"),
    ("LU", "LU280019400644750000","LU28 0019 4006 4475 0000","BCEELULLXXX","Banque Centrale du Luxembourg"),
]

print("Génération cas 4 : domiciliation bancaire étrangère...")
for i in range(1, 11):
    entreprise = get_entreprise(df.sample(1).iloc[0])
    pays_code, iban_raw, iban_fmt, bic, banque_nom = random.choice(IBANS_ETRANGERS)
    ville_court= entreprise["ville"].split()[-1] if entreprise["ville"] else fake.city()

    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"cas4_domiciliation_etrangere_{i:02d}.pdf"),
        titulaire     = entreprise,
        iban_str      = iban_raw,
        iban_formatted= iban_fmt,
        banque_nom    = banque_nom,
        banque_bic    = bic,
        domiciliation = f"{banque_nom} — {pays_code} (domiciliation étrangère)",
        bank_code     = iban_fmt[4:9].replace(" ", ""),
        branch_code   = iban_fmt[9:14].replace(" ", ""),
        account       = iban_raw[14:25] if len(iban_raw) > 14 else "???????????",
        rib_key       = "??",
        anomalie_label= f"DOMICILIATION ÉTRANGÈRE ({pays_code})",
    )
    print(f"  ✓ cas4_domiciliation_etrangere_{i:02d}.pdf")
print("Done ! Cas 4 terminé.\n")


# ─────────────────────────────────────────────
# CAS 5 — IBAN TRONQUÉ / MANQUANT
# Le champ IBAN est absent ou partiellement masqué
# ─────────────────────────────────────────────
print("Génération cas 5 : IBAN tronqué ou manquant...")
for i in range(1, 11):
    entreprise = get_entreprise(df.sample(1).iloc[0])
    iban_data  = generate_iban_fr(fake)
    banque_nom = random.choice(banque_noms)
    banque_bic = BANQUES_FR[banque_nom]
    ville_court= entreprise["ville"].split()[-1] if entreprise["ville"] else fake.city()

    # Soit IBAN vide, soit tronqué à mi-chemin
    mode = random.choice(["vide", "tronque"])
    if mode == "vide":
        iban_affiche = ""
        label = "IBAN MANQUANT"
    else:
        # Garde les 12 premiers caractères et remplace le reste par des étoiles
        iban_affiche = iban_data["iban_formatted"][:14] + " ****"
        label = "IBAN TRONQUÉ"

    build_rib(
        filename      = os.path.join(OUTPUT_DIR, f"cas5_iban_tronque_{i:02d}.pdf"),
        titulaire     = entreprise,
        iban_str      = iban_affiche,
        iban_formatted= iban_affiche,
        banque_nom    = banque_nom,
        banque_bic    = banque_bic,
        domiciliation = f"{banque_nom} — Agence {ville_court}",
        bank_code     = iban_data["bank_code"],
        branch_code   = iban_data["branch_code"],
        account       = iban_data["account"],
        rib_key       = iban_data["rib_key"],
        anomalie_label= label,
    )
    print(f"  ✓ cas5_iban_tronque_{i:02d}.pdf")
print("Done ! Cas 5 terminé.\n")

print(f"Terminé ! 50 RIBs erronés générés dans {OUTPUT_DIR}/")
