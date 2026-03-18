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
random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))

# Charger les vraies entreprises
df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str)
df = df.fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "factures", "valides")
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

def generate_facture(num):
    # Piocher fournisseur et client
    fournisseur = get_entreprise(df.sample(1).iloc[0])
    client = get_entreprise(df.sample(1).iloc[0])

    # Dates
    date_emission = fake.date_between(start_date="-1y", end_date="today")
    date_echeance = date_emission + timedelta(days=random.choice([30, 45, 60]))

    # Lignes de facturation
    nb_lignes = random.randint(1, 5)
    lignes = []
    for _ in range(nb_lignes):
        qte = random.randint(1, 20)
        pu_ht = round(random.uniform(50, 2000), 2)
        total_ht = round(qte * pu_ht, 2)
        lignes.append({
            "description": fake.bs().capitalize(),
            "qte": qte,
            "pu_ht": pu_ht,
            "total_ht": total_ht,
        })

    total_ht = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva = random.choice([0.20, 0.10, 0.055])
    montant_tva = round(total_ht * taux_tva, 2)
    total_ttc = round(total_ht + montant_tva, 2)

    # Générer le PDF
    filename = f"{OUTPUT_DIR}/facture_{num:04d}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    bold = ParagraphStyle("bold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    title_style = ParagraphStyle("title", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16)

    elements = []

    # Titre
    elements.append(Paragraph("FACTURE", title_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"N° {fake.numerify('FACT-####-##')}", bold))
    elements.append(Paragraph(f"Date d'émission : {date_emission.strftime('%d/%m/%Y')}", normal))
    elements.append(Paragraph(f"Date d'échéance : {date_echeance.strftime('%d/%m/%Y')}", normal))
    elements.append(Spacer(1, 0.5*cm))

    # Fournisseur / Client
    info_data = [
        [Paragraph("<b>FOURNISSEUR</b>", bold), Paragraph("<b>CLIENT</b>", bold)],
        [Paragraph(fournisseur["nom"], normal), Paragraph(client["nom"], normal)],
        [Paragraph(fournisseur["adresse"], normal), Paragraph(client["adresse"], normal)],
        [Paragraph(fournisseur["ville"], normal), Paragraph(client["ville"], normal)],
        [Paragraph(f"SIRET : {fournisseur['siret']}", normal), Paragraph(f"SIRET : {client['siret']}", normal)],
        [Paragraph(f"TVA : {fournisseur['tva']}", normal), Paragraph(f"TVA : {client['tva']}", normal)],
    ]
    info_table = Table(info_data, colWidths=[8.5*cm, 8.5*cm])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LINEBELOW", (0,0), (-1,0), 0.5, colors.grey),
        ("TOPPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    # Lignes de facture
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
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(facture_table)
    elements.append(Spacer(1, 0.3*cm))

    # Totaux
    totaux_data = [
        ["", "Total HT :", f"{total_ht:.2f} €"],
        ["", f"TVA ({int(taux_tva*100)}%) :", f"{montant_tva:.2f} €"],
        ["", "Total TTC :", f"{total_ttc:.2f} €"],
    ]
    totaux_table = Table(totaux_data, colWidths=[9*cm, 4*cm, 4.5*cm])
    totaux_table.setStyle(TableStyle([
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,2), (-1,2), "Helvetica-Bold"),
        ("LINEABOVE", (1,2), (-1,2), 0.5, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    elements.append(totaux_table)
    elements.append(Spacer(1, 0.5*cm))

    # Pied de page
    elements.append(Paragraph(f"Règlement par virement bancaire — IBAN : {fake.iban()}", normal))
    elements.append(Paragraph(fake.catch_phrase(), normal))

    doc.build(elements)
    return filename

# Générer 50 factures
NB_FACTURES = 50
print(f"Génération de {NB_FACTURES} factures...")
for i in range(1, NB_FACTURES + 1):
    f = generate_facture(i)
    print(f"  ✓ {f}")

print(f"\nDone ! {NB_FACTURES} factures dans {OUTPUT_DIR}/")