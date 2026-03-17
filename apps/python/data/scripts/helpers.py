"""
helpers.py — utilitaires partagés entre tous les scripts de génération.
Importé par generate_rib, generate_siret, generate_urssaf, generate_kbis, etc.
"""
import random

# ─────────────────────────────────────────────
# BANQUES FRANÇAISES : nom affiché → BIC SWIFT
# ─────────────────────────────────────────────
BANQUES_FR = {
    "BNP Paribas":       "BNPAFRPP",
    "Société Générale":  "SOGEFRPP",
    "Crédit Agricole":   "AGRIFRPP",
    "LCL":               "CRLYFRPP",
    "La Banque Postale": "PSSTFRPPXXX",
    "Caisse d'Épargne":  "CEPAFRPP",
    "Crédit Mutuel":     "CMCIFRPP",
    "CIC":               "CICNFRPP",
    "HSBC France":       "CCFRFRPP",
    "Banque Populaire":  "CCBPFRPP",
    "Boursorama":        "BOUSFRPP",
    "Crédit du Nord":    "NORDFRPP",
}

# ─────────────────────────────────────────────
# FORMES JURIDIQUES
# ─────────────────────────────────────────────
FORMES_JURIDIQUES = [
    "SAS", "SARL", "SA", "EURL", "SASU",
    "SNC", "GIE", "SCOP", "Auto-entrepreneur",
]

# ─────────────────────────────────────────────
# CODES NAF → LIBELLÉS (sous-ensemble représentatif)
# ─────────────────────────────────────────────
CODES_NAF_LIBELLES = {
    "62.01Z": "Programmation informatique",
    "62.02A": "Conseil en systèmes et logiciels informatiques",
    "70.22Z": "Conseil pour les affaires et autres conseils de gestion",
    "73.11Z": "Activités des agences de publicité",
    "41.20A": "Construction de maisons individuelles",
    "47.11F": "Supermarchés",
    "56.10A": "Restauration traditionnelle",
    "81.10Z": "Services de soutien aux bâtiments",
    "85.59B": "Autres enseignements",
    "86.21Z": "Activité des médecins généralistes",
    "45.11Z": "Commerce de voitures et de véhicules automobiles légers",
    "43.21A": "Travaux d'installation électrique dans tous locaux",
    "71.11Z": "Activités d'architecture",
    "80.10Z": "Activités de sécurité privée",
    "49.41A": "Transports routiers de fret interurbains",
}

# ─────────────────────────────────────────────
# RÉGIONS URSSAF : libellé → code à 3 chiffres
# ─────────────────────────────────────────────
REGIONS_URSSAF = {
    "Île-de-France":            "075",
    "Alsace-Moselle":           "067",
    "Aquitaine":                "033",
    "Auvergne":                 "063",
    "Bourgogne":                "021",
    "Bretagne":                 "035",
    "Centre-Val de Loire":      "045",
    "Champagne-Ardenne":        "051",
    "Franche-Comté":            "025",
    "Languedoc-Roussillon":     "034",
    "Limousin":                 "087",
    "Lorraine":                 "057",
    "Midi-Pyrénées":            "031",
    "Nord-Pas-de-Calais":       "059",
    "Normandie":                "076",
    "Pays de la Loire":         "049",
    "Picardie":                 "080",
    "Poitou-Charentes":         "086",
    "Provence-Alpes-Côte d'Azur": "013",
    "Rhône-Alpes":              "069",
}

# ─────────────────────────────────────────────
# IBAN FRANÇAIS — génération avec checksums corrects
# ─────────────────────────────────────────────
def _iban_numeric(s: str) -> str:
    """Convertit une chaîne alphanumérique en chaîne numérique (A=10, B=11…)."""
    result = ""
    for c in s.upper():
        if c.isdigit():
            result += c
        else:
            result += str(ord(c) - ord("A") + 10)
    return result


def generate_iban_fr(fake) -> dict:
    """
    Génère un IBAN français avec check digits ISO 7064 corrects.
    Retourne un dict avec iban, iban_formatted, bank_code, branch_code, account, rib_key.
    """
    bank_code   = fake.numerify("#####")
    branch_code = fake.numerify("#####")
    account     = fake.numerify("###########")
    rib_key     = fake.numerify("##")

    bban = bank_code + branch_code + account + rib_key

    # Calcul des check digits : rearrange = BBAN + "FR00", puis 98 - (mod 97)
    rearranged  = bban + "FR00"
    numeric_str = _iban_numeric(rearranged)
    check       = 98 - (int(numeric_str) % 97)
    check_str   = str(check).zfill(2)

    iban = f"FR{check_str}{bban}"
    formatted = " ".join(iban[i:i+4] for i in range(0, len(iban), 4))

    return {
        "iban":           iban,
        "iban_formatted": formatted,
        "bank_code":      bank_code,
        "branch_code":    branch_code,
        "account":        account,
        "rib_key":        rib_key,
    }


def corrupt_iban_checksum(iban: str) -> str:
    """Retourne l'IBAN avec des check digits délibérément faux."""
    correct_check = iban[2:4]
    # Choisit un check différent du correct
    wrong_check = str(random.randint(1, 97)).zfill(2)
    while wrong_check == correct_check:
        wrong_check = str(random.randint(1, 97)).zfill(2)
    return iban[0:2] + wrong_check + iban[4:]


def format_iban(iban: str) -> str:
    """Formate un IBAN brut en groupes de 4 caractères."""
    return " ".join(iban[i:i+4] for i in range(0, len(iban), 4))


# ─────────────────────────────────────────────
# SIRET — validation et corruption (algorithme de Luhn)
# ─────────────────────────────────────────────
def luhn_checksum(number: str) -> int:
    """Calcule le checksum de Luhn sur une chaîne de chiffres."""
    digits = [int(d) for d in number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10


def is_luhn_valid(number: str) -> bool:
    return luhn_checksum(number) == 0


# ─────────────────────────────────────────────
# KBIS — tribunaux de commerce et fonctions dirigeants
# ─────────────────────────────────────────────
TRIBUNAUX_COMMERCE = [
    "Paris", "Lyon", "Marseille", "Bordeaux", "Lille",
    "Nantes", "Toulouse", "Strasbourg", "Nice", "Rennes",
    "Grenoble", "Montpellier", "Rouen", "Toulon", "Clermont-Ferrand",
    "Nancy", "Dijon", "Angers", "Caen", "Orléans",
]

FONCTIONS_DIRIGEANT = [
    "Gérant",
    "Président",
    "Directeur Général",
    "Président du Conseil d'Administration",
    "Co-gérant",
    "Directeur Général Délégué",
]


def corrupt_siret(siret: str) -> str:
    """Retourne un SIRET avec le dernier chiffre modifié pour invalider le checksum Luhn."""
    last = int(siret[-1])
    wrong = (last + random.randint(1, 9)) % 10
    return siret[:-1] + str(wrong)
