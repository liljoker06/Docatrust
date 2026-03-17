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
random.seed(55)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

df = pd.read_csv(os.path.join(DATA_DIR, "raw", "entreprises_sample.csv"), dtype=str).fillna("")

OUTPUT_DIR = os.path.join(DATA_DIR, "devis", "erronees")
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

def build_pdf(filename, prestataire, client, date_emission, date_validite,
              duree_validite, lignes, total_ht, montant_tva, total_ttc,
              taux_tva, numero_devis=None, anomalie_label=None):
    """Fonction générique de construction PDF — réutilisée pour tous les cas."""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    bold         = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10)
    normal       = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    title_style  = ParagraphStyle("title",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16)
    status_style = ParagraphStyle("status", parent=styles["Normal"], fontName="Helvetica-Bold",
                                  fontSize=9, textColor=colors.HexColor("#e67e22"))
    red_style    = ParagraphStyle("red",    parent=styles["Normal"], fontSize=8,
                                  textColor=colors.HexColor("#cc0000"))

    elements = []

    elements.append(Paragraph("DEVIS", title_style))
    elements.append(Paragraph("EN ATTENTE DE VALIDATION", status_style))
    if anomalie_label:
        elements.append(Paragraph(f"[TEST - {anomalie_label}]", red_style))
    elements.append(Spacer(1, 0.3*cm))

    # Numéro de devis : peut être absent (cas 3)
    if numero_devis:
        elements.append(Paragraph(f"N° {numero_devis}", bold))
    elements.append(Paragraph(f"Date d'émission : {date_emission.strftime('%d/%m/%Y')}", normal))
    if date_validite:
        elements.append(Paragraph(f"Valable jusqu'au : {date_validite.strftime('%d/%m/%Y')} ({duree_validite} jours)", normal))
    elements.append(Spacer(1, 0.5*cm))

    info_data = [
        [Paragraph("<b>PRESTATAIRE</b>", bold), Paragraph("<b>CLIENT</b>", bold)],
        [Paragraph(prestataire["nom"], normal),  Paragraph(client["nom"], normal)],
        [Paragraph(prestataire["adresse"], normal), Paragraph(client["adresse"], normal)],
        [Paragraph(prestataire["ville"], normal),   Paragraph(client["ville"], normal)],
        [Paragraph(f"SIRET : {prestataire['siret']}", normal), Paragraph(f"SIRET : {client['siret']}", normal)],
        [Paragraph(f"TVA : {prestataire['tva']}", normal),     Paragraph(f"TVA : {client['tva']}", normal)],
    ]
    info_table = Table(info_data, colWidths=[8.5*cm, 8.5*cm])
    info_table.setStyle(TableStyle([
        ("VALIGN",    (0,0), (-1,-1), "TOP"),
        ("LINEBELOW", (0,0), (-1, 0), 0.5, colors.grey),
        ("TOPPADDING",(0,0), (-1,-1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    table_data = [["Désignation", "Qté", "PU HT (€)", "Total HT (€)"]]
    for l in lignes:
        table_data.append([
            Paragraph(l["description"], normal),
            str(l["qte"]),
            f"{l['pu_ht']:.2f}",
            f"{l['total_ht']:.2f}",
        ])
    devis_table = Table(table_data, colWidths=[9*cm, 2*cm, 3.5*cm, 3*cm])
    devis_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e67e22")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fef9f5")]),
        ("GRID",  (0,0), (-1,-1), 0.3, colors.grey),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(devis_table)
    elements.append(Spacer(1, 0.3*cm))

    totaux_data = [
        ["", "Total HT :",                    f"{total_ht:.2f} €"],
        ["", f"TVA ({int(taux_tva*100)}%) :", f"{montant_tva:.2f} €"],
        ["", "Total TTC :",                   f"{total_ttc:.2f} €"],
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

    elements.append(Paragraph(
        f"Ce devis est valable {duree_validite} jours à compter de sa date d'émission.", normal))
    elements.append(Paragraph(
        "Pour accepter ce devis, merci de nous retourner un exemplaire signé avec la mention 'Bon pour accord'.", normal))

    doc.build(elements)

def base_lignes():
    nb = random.randint(1, 4)
    lignes = []
    for _ in range(nb):
        qte   = random.randint(1, 20)
        pu_ht = round(random.uniform(50, 2000), 2)
        lignes.append({"description": fake.bs().capitalize(),
                       "qte": qte, "pu_ht": pu_ht,
                       "total_ht": round(qte * pu_ht, 2)})
    return lignes

# ─────────────────────────────────────────────
# CAS 1 — DATE DE VALIDITÉ EXPIRÉE
# Le devis affiche une date de validité dans le passé
# ─────────────────────────────────────────────
print("Génération cas 1 : date de validité expirée...")
for i in range(1, 11):
    prestataire = get_entreprise(df.sample(1).iloc[0])
    client      = get_entreprise(df.sample(1).iloc[0])
    duree_validite = random.choice([30, 45, 60])
    # Date d'émission dans le passé lointain → validité forcément expirée
    date_emission = fake.date_between(start_date="-3y", end_date="-1y")
    date_validite = date_emission + timedelta(days=duree_validite)
    lignes      = base_lignes()
    total_ht    = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva    = random.choice([0.20, 0.10, 0.055])
    montant_tva = round(total_ht * taux_tva, 2)
    total_ttc   = round(total_ht + montant_tva, 2)

    build_pdf(
        filename       = f"{OUTPUT_DIR}/cas1_validite_expiree_{i:02d}.pdf",
        prestataire    = prestataire,
        client         = client,
        date_emission  = date_emission,
        date_validite  = date_validite,
        duree_validite = duree_validite,
        lignes         = lignes,
        total_ht       = total_ht,
        montant_tva    = montant_tva,
        total_ttc      = total_ttc,
        taux_tva       = taux_tva,
        numero_devis   = fake.numerify("DEVIS-####-##"),
        anomalie_label = "VALIDITE EXPIREE"
    )
    print(f"  ✓ cas1_validite_expiree_{i:02d}.pdf")
print("Done ! Cas 1 terminé.\n")

# ─────────────────────────────────────────────
# CAS 2 — TOTAUX INCOHÉRENTS
# Le total HT affiché ne correspond pas à la somme des lignes
# ─────────────────────────────────────────────
print("Génération cas 2 : totaux incohérents...")
for i in range(1, 11):
    prestataire    = get_entreprise(df.sample(1).iloc[0])
    client         = get_entreprise(df.sample(1).iloc[0])
    duree_validite = random.choice([30, 45, 60])
    date_emission  = fake.date_between(start_date="-6m", end_date="today")
    date_validite  = date_emission + timedelta(days=duree_validite)
    lignes         = base_lignes()
    total_ht_reel  = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva       = random.choice([0.20, 0.10, 0.055])

    # Total HT volontairement faux (écart aléatoire)
    ecart          = round(random.uniform(50, 500) * random.choice([-1, 1]), 2)
    total_ht_faux  = round(total_ht_reel + ecart, 2)
    montant_tva    = round(total_ht_faux * taux_tva, 2)
    total_ttc      = round(total_ht_faux + montant_tva, 2)

    build_pdf(
        filename       = f"{OUTPUT_DIR}/cas2_totaux_incoherents_{i:02d}.pdf",
        prestataire    = prestataire,
        client         = client,
        date_emission  = date_emission,
        date_validite  = date_validite,
        duree_validite = duree_validite,
        lignes         = lignes,
        total_ht       = total_ht_faux,   # ← affiché mais faux
        montant_tva    = montant_tva,
        total_ttc      = total_ttc,
        taux_tva       = taux_tva,
        numero_devis   = fake.numerify("DEVIS-####-##"),
        anomalie_label = "TOTAUX INCOHERENTS"
    )
    print(f"  ✓ cas2_totaux_incoherents_{i:02d}.pdf")
print("Done ! Cas 2 terminé.\n")

# ─────────────────────────────────────────────
# CAS 3 — NUMÉRO DE DEVIS MANQUANT
# Le champ numéro de devis est absent
# ─────────────────────────────────────────────
print("Génération cas 3 : numéro de devis manquant...")
for i in range(1, 11):
    prestataire    = get_entreprise(df.sample(1).iloc[0])
    client         = get_entreprise(df.sample(1).iloc[0])
    duree_validite = random.choice([30, 45, 60])
    date_emission  = fake.date_between(start_date="-6m", end_date="today")
    date_validite  = date_emission + timedelta(days=duree_validite)
    lignes         = base_lignes()
    total_ht       = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva       = random.choice([0.20, 0.10, 0.055])
    montant_tva    = round(total_ht * taux_tva, 2)
    total_ttc      = round(total_ht + montant_tva, 2)

    build_pdf(
        filename       = f"{OUTPUT_DIR}/cas3_numero_manquant_{i:02d}.pdf",
        prestataire    = prestataire,
        client         = client,
        date_emission  = date_emission,
        date_validite  = date_validite,
        duree_validite = duree_validite,
        lignes         = lignes,
        total_ht       = total_ht,
        montant_tva    = montant_tva,
        total_ttc      = total_ttc,
        taux_tva       = taux_tva,
        numero_devis   = None,             # ← absent volontairement
        anomalie_label = "NUMERO MANQUANT"
    )
    print(f"  ✓ cas3_numero_manquant_{i:02d}.pdf")
print("Done ! Cas 3 terminé.\n")

# ─────────────────────────────────────────────
# CAS 4 — REMISE ILLOGIQUE
# Une remise dépasse 100% ou rend le total négatif
# ─────────────────────────────────────────────
print("Génération cas 4 : remise illogique...")
for i in range(1, 11):
    prestataire    = get_entreprise(df.sample(1).iloc[0])
    client         = get_entreprise(df.sample(1).iloc[0])
    duree_validite = random.choice([30, 45, 60])
    date_emission  = fake.date_between(start_date="-6m", end_date="today")
    date_validite  = date_emission + timedelta(days=duree_validite)
    lignes         = base_lignes()
    total_ht_brut  = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva       = random.choice([0.20, 0.10, 0.055])

    # Remise aberrante : entre 110% et 200%
    taux_remise    = round(random.uniform(1.1, 2.0), 2)
    remise         = round(total_ht_brut * taux_remise, 2)
    total_ht       = round(total_ht_brut - remise, 2)   # ← négatif
    montant_tva    = round(total_ht * taux_tva, 2)
    total_ttc      = round(total_ht + montant_tva, 2)

    # Ajout d'une ligne remise dans les lignes affichées
    lignes_affichees = lignes + [{
        "description": f"Remise commerciale ({int(taux_remise * 100)}%)",
        "qte": 1,
        "pu_ht": -remise,
        "total_ht": -remise,
    }]

    build_pdf(
        filename       = f"{OUTPUT_DIR}/cas4_remise_illogique_{i:02d}.pdf",
        prestataire    = prestataire,
        client         = client,
        date_emission  = date_emission,
        date_validite  = date_validite,
        duree_validite = duree_validite,
        lignes         = lignes_affichees,
        total_ht       = total_ht,
        montant_tva    = montant_tva,
        total_ttc      = total_ttc,
        taux_tva       = taux_tva,
        numero_devis   = fake.numerify("DEVIS-####-##"),
        anomalie_label = "REMISE ILLOGIQUE"
    )
    print(f"  ✓ cas4_remise_illogique_{i:02d}.pdf")
print("Done ! Cas 4 terminé.\n")

# ─────────────────────────────────────────────
# CAS 5 — PRESTATAIRE IDENTIQUE AU CLIENT
# La même entreprise est à la fois émetteur et destinataire
# ─────────────────────────────────────────────
print("Génération cas 5 : prestataire = client...")
for i in range(1, 11):
    # Même entreprise des deux côtés
    entreprise     = get_entreprise(df.sample(1).iloc[0])
    duree_validite = random.choice([30, 45, 60])
    date_emission  = fake.date_between(start_date="-6m", end_date="today")
    date_validite  = date_emission + timedelta(days=duree_validite)
    lignes         = base_lignes()
    total_ht       = round(sum(l["total_ht"] for l in lignes), 2)
    taux_tva       = random.choice([0.20, 0.10, 0.055])
    montant_tva    = round(total_ht * taux_tva, 2)
    total_ttc      = round(total_ht + montant_tva, 2)

    build_pdf(
        filename       = f"{OUTPUT_DIR}/cas5_prestataire_egal_client_{i:02d}.pdf",
        prestataire    = entreprise,
        client         = entreprise,   # ← même entreprise
        date_emission  = date_emission,
        date_validite  = date_validite,
        duree_validite = duree_validite,
        lignes         = lignes,
        total_ht       = total_ht,
        montant_tva    = montant_tva,
        total_ttc      = total_ttc,
        taux_tva       = taux_tva,
        numero_devis   = fake.numerify("DEVIS-####-##"),
        anomalie_label = "PRESTATAIRE = CLIENT"
    )
    print(f"  ✓ cas5_prestataire_egal_client_{i:02d}.pdf")
print("Done ! Cas 5 terminé.\n")

print(f"Terminé ! 50 devis erronés générés dans {OUTPUT_DIR}/")
