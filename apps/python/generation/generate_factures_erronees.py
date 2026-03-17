import pandas as pd
import random
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime, timedelta
import os

fake = Faker('fr_FR')
random.seed(99)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "factures", "erronees")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_entreprise(row):
    nom = row.get("denominationUniteLegale", "").strip()
    if not nom:
        nom = f"{row.get('nomUniteLegale','')} {row.get('prénomUsuelUniteLegale','')}".strip()
    if not nom:
        nom = fake.company()
    adresse = f"{row.get('numeroVoieEtablissement','')} {row.get('typeVoieEtablissement','')} {row.get('libelleVoieEtablissement','')}".strip()
    ville = f"{row.get('codePostalEtablissement','')} {row.get('libelleCommuneEtablissement','')}".strip()
    return {
        "nom": nom,
        "siret": row.get("siret", fake.numerify("##############")),
        "adresse": adresse if adresse else fake.street_address(),
        "ville": ville if ville else fake.city(),
        "tva": f"FR{fake.numerify('##')}{row.get('siren','')[0:9]}",
    }

def build_pdf(filename, fournisseur, client, date_emission, date_echeance,
              lignes, total_ht, montant_tva, total_ttc, taux_tva,
              numero_facture=None, anomalie_label=None):
    """Fonction générique de construction PDF — réutilisée pour tous les cas."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    bold   = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    title_style = ParagraphStyle("title", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16)
    red_style   = ParagraphStyle("red",   parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#cc0000"))

    elements = []

    elements.append(Paragraph("FACTURE", title_style))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.3*cm))
    if numero_facture:
        elements.append(Paragraph(f"N° {numero_facture}", bold))
    elements.append(Paragraph(f"Date d'émission : {date_emission.strftime('%d/%m/%Y')}", normal))
    elements.append(Paragraph(f"Date d'échéance : {date_echeance.strftime('%d/%m/%Y')}", normal))
    elements.append(Spacer(1, 0.5*cm))

    info_data = [
        [Paragraph("<b>FOURNISSEUR</b>", bold), Paragraph("<b>CLIENT</b>", bold)],
        [Paragraph(fournisseur["nom"], normal),  Paragraph(client["nom"], normal)],
        [Paragraph(fournisseur["adresse"], normal), Paragraph(client["adresse"], normal)],
        [Paragraph(fournisseur["ville"], normal),   Paragraph(client["ville"], normal)],
        [Paragraph(f"SIRET : {fournisseur['siret']}", normal), Paragraph(f"SIRET : {client['siret']}", normal)],
        [Paragraph(f"TVA : {fournisseur['tva']}", normal),     Paragraph(f"TVA : {client['tva']}", normal)],
    ]
    info_table = Table(info_data, colWidths=[8.5*cm, 8.5*cm])
    info_table.setStyle(TableStyle([
        ("VALIGN",    (0,0), (-1,-1), "TOP"),
        ("LINEBELOW", (0,0), (-1, 0), 0.5, colors.grey),
        ("TOPPADDING",(0,0), (-1,-1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    table_data = [["Description", "Qté", "PU HT (€)", "Total HT (€)"]]
    for l in lignes:
        table_data.append([
            Paragraph(l["description"], normal),
            str(l["qte"]),
            f"{l['pu_ht']:.2f}",
            f"{l['total_ht']:.2f}",
        ])
    facture_table = Table(table_data, colWidths=[9*cm, 2*cm, 3.5*cm, 3*cm])
    facture_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("GRID",   (0,0), (-1,-1), 0.3, colors.grey),
        ("ALIGN",  (1,0), (-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(facture_table)
    elements.append(Spacer(1, 0.3*cm))

    totaux_data = [
        ["", "Total HT :",          f"{total_ht:.2f} €"],
        ["", f"TVA ({int(taux_tva*100)}%) :", f"{montant_tva:.2f} €"],
        ["", "Total TTC :",         f"{total_ttc:.2f} €"],
    ]
    totaux_table = Table(totaux_data, colWidths=[9*cm, 4*cm, 4.5*cm])
    totaux_table.setStyle(TableStyle([
        ("ALIGN",    (1,0), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,2), (-1, 2), "Helvetica-Bold"),
        ("LINEABOVE",(1,2), (-1, 2), 0.5, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    elements.append(totaux_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Règlement par virement bancaire — IBAN : {fake.iban()}", normal))

    doc.build(elements)

def base_lignes():
    nb = random.randint(1, 4)
    lignes = []
    for _ in range(nb):
        qte    = random.randint(1, 20)
        pu_ht  = round(random.uniform(50, 2000), 2)
        lignes.append({"description": fake.bs().capitalize(),
                       "qte": qte, "pu_ht": pu_ht,
                       "total_ht": round(qte * pu_ht, 2)})
    return lignes

# ─────────────────────────────────────────────
# CAS 1 — TVA INCOHÉRENTE
# Le taux TVA affiché ne correspond pas au montant calculé
# ─────────────────────────────────────────────
print("Génération cas 1 : TVA incohérente...")
for i in range(1, 11):
    fournisseur   = get_entreprise(df.sample(1).iloc[0])
    client        = get_entreprise(df.sample(1).iloc[0])
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=30)
    lignes        = base_lignes()
    total_ht      = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva      = random.choice([0.20, 0.10, 0.055])

    # TVA volontairement fausse (mauvais taux appliqué)
    faux_taux   = random.choice([t for t in [0.20, 0.10, 0.055] if t != taux_tva])
    montant_tva = round(total_ht * faux_taux, 2)   # ← incohérent avec taux_tva affiché
    total_ttc   = round(total_ht + montant_tva, 2)

    build_pdf(
        filename        = f"{OUTPUT_DIR}/cas1_tva_incoherente_{i:02d}.pdf",
        fournisseur     = fournisseur,
        client          = client,
        date_emission   = date_emission,
        date_echeance   = date_echeance,
        lignes          = lignes,
        total_ht        = total_ht,
        montant_tva     = montant_tva,
        total_ttc       = total_ttc,
        taux_tva        = taux_tva,
        numero_facture  = fake.numerify("FACT-####-##"),
        anomalie_label  = "TVA INCOHERENTE"
    )
    print(f"  ✓ cas1_tva_incoherente_{i:02d}.pdf")
print("Done ! Cas 1 terminé.\n")

# ─────────────────────────────────────────────
# CAS 2 — TOTAUX INCOHÉRENTS
# Le total HT affiché ne correspond pas à la somme des lignes
# ─────────────────────────────────────────────
print("Génération cas 2 : totaux incohérents...")
for i in range(1, 11):
    fournisseur   = get_entreprise(df.sample(1).iloc[0])
    client        = get_entreprise(df.sample(1).iloc[0])
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=30)
    lignes        = base_lignes()
    total_ht_reel = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva      = random.choice([0.20, 0.10, 0.055])

    # Total HT volontairement faux (écart aléatoire)
    ecart         = round(random.uniform(50, 500) * random.choice([-1, 1]), 2)
    total_ht_faux = round(total_ht_reel + ecart, 2)
    montant_tva   = round(total_ht_faux * taux_tva, 2)
    total_ttc     = round(total_ht_faux + montant_tva, 2)

    build_pdf(
        filename        = f"{OUTPUT_DIR}/cas2_totaux_incoherents_{i:02d}.pdf",
        fournisseur     = fournisseur,
        client          = client,
        date_emission   = date_emission,
        date_echeance   = date_echeance,
        lignes          = lignes,
        total_ht        = total_ht_faux,   # ← affiché mais faux
        montant_tva     = montant_tva,
        total_ttc       = total_ttc,
        taux_tva        = taux_tva,
        numero_facture  = fake.numerify("FACT-####-##"),
        anomalie_label  = "TOTAUX INCOHERENTS"
    )
    print(f"  ✓ cas2_totaux_incoherents_{i:02d}.pdf")
print("Done ! Cas 2 terminé.\n")

# ─────────────────────────────────────────────
# CAS 3 — NUMÉRO DE FACTURE MANQUANT
# Le champ numéro de facture est absent
# ─────────────────────────────────────────────
print("Génération cas 3 : numéro de facture manquant...")
for i in range(1, 11):
    fournisseur   = get_entreprise(df.sample(1).iloc[0])
    client        = get_entreprise(df.sample(1).iloc[0])
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=30)
    lignes        = base_lignes()
    total_ht      = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva      = random.choice([0.20, 0.10, 0.055])
    montant_tva   = round(total_ht * taux_tva, 2)
    total_ttc     = round(total_ht + montant_tva, 2)

    build_pdf(
        filename        = f"{OUTPUT_DIR}/cas3_numero_manquant_{i:02d}.pdf",
        fournisseur     = fournisseur,
        client          = client,
        date_emission   = date_emission,
        date_echeance   = date_echeance,
        lignes          = lignes,
        total_ht        = total_ht,
        montant_tva     = montant_tva,
        total_ttc       = total_ttc,
        taux_tva        = taux_tva,
        numero_facture  = None,            # ← absent volontairement
        anomalie_label  = "NUMERO MANQUANT"
    )
    print(f"  ✓ cas3_numero_manquant_{i:02d}.pdf")
print("Done ! Cas 3 terminé.\n")

# ─────────────────────────────────────────────
# CAS 4 — REMISE ILLOGIQUE
# Une remise dépasse 100% et rend le total négatif
# ─────────────────────────────────────────────
print("Génération cas 4 : remise illogique...")
for i in range(1, 11):
    fournisseur   = get_entreprise(df.sample(1).iloc[0])
    client        = get_entreprise(df.sample(1).iloc[0])
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=30)
    lignes        = base_lignes()
    total_ht_brut = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva      = random.choice([0.20, 0.10, 0.055])

    # Remise aberrante : entre 110% et 200%
    taux_remise = round(random.uniform(1.1, 2.0), 2)
    remise      = round(total_ht_brut * taux_remise, 2)
    total_ht    = round(total_ht_brut - remise, 2)   # ← négatif
    montant_tva = round(total_ht * taux_tva, 2)
    total_ttc   = round(total_ht + montant_tva, 2)

    lignes_affichees = lignes + [{
        "description": f"Remise commerciale ({int(taux_remise * 100)}%)",
        "qte": 1,
        "pu_ht": -remise,
        "total_ht": -remise,
    }]

    build_pdf(
        filename        = f"{OUTPUT_DIR}/cas4_remise_illogique_{i:02d}.pdf",
        fournisseur     = fournisseur,
        client          = client,
        date_emission   = date_emission,
        date_echeance   = date_echeance,
        lignes          = lignes_affichees,
        total_ht        = total_ht,
        montant_tva     = montant_tva,
        total_ttc       = total_ttc,
        taux_tva        = taux_tva,
        numero_facture  = fake.numerify("FACT-####-##"),
        anomalie_label  = "REMISE ILLOGIQUE"
    )
    print(f"  ✓ cas4_remise_illogique_{i:02d}.pdf")
print("Done ! Cas 4 terminé.\n")

# ─────────────────────────────────────────────
# CAS 5 — FOURNISSEUR IDENTIQUE AU CLIENT
# La même entreprise est à la fois émetteur et destinataire
# ─────────────────────────────────────────────
print("Génération cas 5 : fournisseur = client...")
for i in range(1, 11):
    # Même entreprise des deux côtés
    entreprise    = get_entreprise(df.sample(1).iloc[0])
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=30)
    lignes        = base_lignes()
    total_ht      = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva      = random.choice([0.20, 0.10, 0.055])
    montant_tva   = round(total_ht * taux_tva, 2)
    total_ttc     = round(total_ht + montant_tva, 2)

    build_pdf(
        filename        = f"{OUTPUT_DIR}/cas5_fournisseur_egal_client_{i:02d}.pdf",
        fournisseur     = entreprise,
        client          = entreprise,   # ← même entreprise
        date_emission   = date_emission,
        date_echeance   = date_echeance,
        lignes          = lignes,
        total_ht        = total_ht,
        montant_tva     = montant_tva,
        total_ttc       = total_ttc,
        taux_tva        = taux_tva,
        numero_facture  = fake.numerify("FACT-####-##"),
        anomalie_label  = "FOURNISSEUR = CLIENT"
    )
    print(f"  ✓ cas5_fournisseur_egal_client_{i:02d}.pdf")
print("Done ! Cas 5 terminé.\n")

print(f"Terminé ! 50 factures erronées générées dans {OUTPUT_DIR}/")


