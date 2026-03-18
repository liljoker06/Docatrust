Contexte :

Les entreprises traitent quotidiennement des milliers de documents administratifs :



Factures fournisseurs

Devis

Attestation SIRET

Attestation de vigilance URSSAF

Extrait Kbis

RIB

Ces documents sont :



hétérogènes

non structurés

parfois scannés de mauvaise qualité

juridiquement engageants

Un opérateur doit :



Lire les documents

Extraire les informations clés

Vérifier la cohérence

Saisir les données dans plusieurs systèmes internes

Valider la conformité réglementaire

Ce processus est chronophage, sujet aux erreurs, et non scalable



Missions :

Développer une plateforme permettant :



Upload de pièces comptables (PDF, images) → Stockage brut une BDD NoSQL ou Data Lake (si le module est déjà vu)

Les classifier automatiquement : factures, devis, etc.

Extraction des informations clés via OCR (par ex, Tesseract) :

SIRET

TVA

Montant HT / TTC

Date d’émission

Date d’expiration Attestation

Vérification intelligente des incohérences inter-documents :

Détection incohérence SIRET entre facture et attestation

Détection date expiration dépassée

Après l’OCR, pensez toujours pour le stockage, à une BDD NoSQL ou un Data Lake structuré en 3 zones :

Raw zone : documents bruts

Clean zone : texte OCR

Curated zone : données structurées

Remplissage automatique de 2 front-ends ; applications métiers, par exemple :

CRM et Outil de conformité

ou éventuellemnt une base fournisseur

être conteneurisée

Reposer sur une Orchestration AirFlow (si le module est déjà vu)



Fonctionnalités obligatoires :

Upload multi-documents

Classification automatique du type de document

OCR robuste

Vérification cohérence inter-documents

Auto-remplissage de 2 applications simulées

Stockage Data Lake structuré en 3 zones

Pipeline orchestré avec AirFlow



Architecture cible attendue :

Ingestion

Upload → Stockage brut Data Lake

Orchestration, Airflow pour pipeline

Ingestion

OCR

Extraction

Validation

Stockage

Raw zone : documents bruts

Clean zone : texte OCR

Curated zone : données structurées