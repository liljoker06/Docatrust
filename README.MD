# DocaTrust — Plateforme de conformité documentaire

DocaTrust est une plateforme complète d'analyse, de validation et de traitement de documents métier (factures, devis, Kbis, RIB, URSSAF, SIRET) propulsée par l'IA. Elle combine OCR, extraction de données, vérification SIRENE et orchestration de pipeline automatisé.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTENDS                                  │
│                                                                     │
│   web (React/Vite)          web-admin (React/Vite)                  │
│   :3000 — Client CRM        :3001 — Back-office admin               │
└───────────────┬─────────────────────────┬───────────────────────────┘
                │                         │
                ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                     API Node.js (Express)  :4000                  │
│  Auth · Upload · Documents · Admin · Pipeline trigger             │
└──────┬──────────────┬────────────────────────┬────────────────────┘
       │              │                        │
       ▼              ▼                        ▼
┌────────────┐ ┌─────────────┐      ┌──────────────────┐
│ PostgreSQL │ │    MinIO    │      │ Python FastAPI   │
│   :5432    │ │ :9000/:9001 │      │     :8000        │
│  Metadata  │ │  Data Lake  │      │  OCR · SIRENE    │
│  Logs      │ │raw/clean/   │      │  NLP · Extract   │
│            │ │curated      │      └──────────────────┘
└────────────┘ └──────┬──────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Apache Airflow  :8080                          │
│  DAG: document_pipeline                                         │
│  ingest → OCR → validate → save_results                         │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│    Redis     │
│    :6379     │
│  Queue/Cache │
└──────────────┘
```

---

## Services

| Service | Container | Port(s) | Description |
|---|---|---|---|
| `web` | hackaton-web | **3000** | Frontend client (React/Vite) |
| `web-admin` | hackaton-web-admin | **3001** | Interface d'administration (React/Vite) |
| `api` | hackaton-api | **4000** | API REST Node.js/Express |
| `python` | hackaton-python | **8000** | FastAPI — OCR, extraction, SIRENE |
| `postgres` | hackaton-postgres | **5432** | Base de données PostgreSQL |
| `pgadmin` | hackaton-pgadmin | **5050** | Interface web PgAdmin |
| `minio` | hackaton-minio | **9000** / **9001** | Stockage objet S3 / Console |
| `redis` | hackaton-redis | **6379** | Cache et file de tâches |
| `airflow-webserver` | hackaton-airflow-webserver | **8080** | Interface Airflow (DAGs, runs) |
| `airflow-scheduler` | hackaton-airflow-scheduler | — | Ordonnanceur Airflow |

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20
- 8 Go de RAM recommandés (PaddleOCR est gourmand)

---

## Installation et lancement

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd hackaton
```

### 2. Configurer les variables d'environnement

Copier chaque fichier `.env.example` en `.env` et renseigner les valeurs :

```bash
# Racine du projet (MinIO + Airflow)
cp .env.example .env

# API Node.js
cp apps/api/.env.example apps/api/.env

# Python FastAPI (clé INSEE)
cp apps/python/.env.example apps/python/.env

# Frontend client
cp apps/web/.env.example apps/web/.env

# Frontend admin
cp apps/web-admin/.env.example apps/web-admin/.env
```

> Voir la section **Variables d'environnement** ci-dessous pour le détail de chaque variable.

### 3. Lancer la stack complète

```bash
docker compose -f docker-compose.dev.yaml up --build
```

Premier démarrage : Airflow initialise sa base de données, MinIO crée les buckets `raw`, `clean` et `curated`. Prévoir ~2 min.

### 4. Lancer uniquement certains services

```bash
# Uniquement le backend + BDD
docker compose -f docker-compose.dev.yaml up --build api postgres redis minio minio-init

# Uniquement le frontend client
docker compose -f docker-compose.dev.yaml up --build web

# Rebuild d'un seul service après modification du code
docker compose -f docker-compose.dev.yaml up --build python
```

### 5. Arrêter la stack

```bash
# Arrêter sans supprimer les volumes (données conservées)
docker compose -f docker-compose.dev.yaml down

# Arrêter ET supprimer toutes les données persistantes
docker compose -f docker-compose.dev.yaml down -v
```

---

## Variables d'environnement

### `.env` — Racine du projet

> Partagé par Airflow et MinIO via docker-compose.

| Variable | Description | Exemple |
|---|---|---|
| `MINIO_ROOT_USER` | Nom d'utilisateur admin MinIO | `minioadmin` |
| `MINIO_ROOT_PASSWORD` | Mot de passe admin MinIO | `changeme` |
| `AIRFLOW_DB_USER` | Utilisateur de la base Airflow | `airflow` |
| `AIRFLOW_DB_PASSWORD` | Mot de passe de la base Airflow | `airflow` |
| `AIRFLOW_USER` | Identifiant de l'UI Airflow | `api_user` |
| `AIRFLOW_PASSWORD` | Mot de passe de l'UI Airflow | `changeme` |
| `AIRFLOW_EMAIL` | Email admin Airflow | `admin@example.com` |

---

### `apps/api/.env` — API Node.js

| Variable | Description | Exemple |
|---|---|---|
| `PORT` | Port de l'API | `4000` |
| `NODE_ENV` | Environnement Node | `development` |
| `DB_HOST` | Hôte PostgreSQL (nom du container) | `postgres` |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `DB_NAME` | Nom de la base de données | `pyra_data` |
| `DB_USER` | Utilisateur PostgreSQL | `postgres` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `postgres` |
| `PGADMIN_EMAIL` | Email de connexion PgAdmin | `admin@admin.com` |
| `PGADMIN_PASSWORD` | Mot de passe PgAdmin | `admin` |
| `TOKEN_API_ACCESS_EXPIRES_IN` | Durée des tokens JWT (en heures) | `8` |
| `BCRYPT_SALT_ROUNDS` | Rounds de hashage bcrypt | `10` |
| `MINIO_ENDPOINT` | Hôte MinIO (interne Docker) | `minio` |
| `MINIO_PORT` | Port MinIO | `9000` |
| `MINIO_USE_SSL` | Activer SSL pour MinIO | `false` |
| `MINIO_ACCESS_KEY` | Clé d'accès MinIO (= MINIO_ROOT_USER) | `minioadmin` |
| `MINIO_SECRET_KEY` | Clé secrète MinIO (= MINIO_ROOT_PASSWORD) | `changeme` |
| `MINIO_BUCKET_RAW` | Bucket des documents bruts | `raw` |
| `MINIO_BUCKET_CLEAN` | Bucket après traitement OCR | `clean` |
| `MINIO_BUCKET_CURATED` | Bucket après validation | `curated` |
| `AIRFLOW_URL` | URL Airflow (interne Docker) | `http://airflow-webserver:8080` |
| `AIRFLOW_USER` | Utilisateur Airflow (= racine) | `api_user` |
| `AIRFLOW_PASSWORD` | Mot de passe Airflow (= racine) | `changeme` |
| `PYTHON_API_URL` | URL FastAPI Python (interne Docker) | `http://python:8000` |

---

### `apps/python/.env` — FastAPI Python

| Variable | Description | Exemple |
|---|---|---|
| `INSEE_API_KEY_INTEGRATION` | Clé API INSEE SIRENE — obtenir sur [api.insee.fr](https://api.insee.fr) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `INSEE_SIRENE_BASE_URL` | URL de base de l'API SIRENE | `https://api.insee.fr/api-sirene/3.11` |

---

### `apps/web/.env` — Frontend client (React/Vite)

| Variable | Description | Exemple |
|---|---|---|
| `VITE_API_URL` | URL publique de l'API Node.js | `http://localhost:4000` |
| `VITE_PYTHON_API_URL` | URL publique de la FastAPI Python | `http://localhost:8000` |

---

### `apps/web-admin/.env` — Frontend admin (React/Vite)

| Variable | Description | Exemple |
|---|---|---|
| `VITE_API_URL` | URL publique de l'API Node.js | `http://localhost:4000` |

---

## Pipeline documentaire

```
Upload fichier (web :3000)
        │
        ▼
POST /api/documents/upload  (api :4000)
  → Stockage MinIO bucket raw
  → Enregistrement BDD (status: RAW)
  → Déclenchement DAG Airflow
        │
        ▼
DAG: document_pipeline  (airflow :8080)
  1. ingest       — Récupère le fichier depuis MinIO raw
  2. ocr          — Envoie à Python FastAPI → PaddleOCR → extraction champs
  3. validate     — Vérification SIRENE INSEE, calcul des alertes de conformité
  4. save_results — Stocke le JSON dans MinIO clean/curated
                 — Met à jour le status en BDD (RAW → CLEAN → CURATED)
        │
        ▼
Résultats accessibles :
  GET /api/documents/:id/result    — JSON extrait + alertes
  GET /api/documents/:id/download  — Fichier original
```

---

## Interfaces disponibles

| Interface | URL | Description |
|---|---|---|
| **Frontend client** | http://localhost:3000 | Upload, tableau de bord, suivi documents |
| **Frontend admin** | http://localhost:3001 | Gestion utilisateurs, alertes, logs, fournisseurs |
| **API REST** | http://localhost:4000 | Node.js Express — Auth, documents, admin |
| **FastAPI docs** | http://localhost:8000/docs | Documentation Swagger auto-générée |
| **Airflow UI** | http://localhost:8080 | Visualisation et gestion des DAGs |
| **MinIO Console** | http://localhost:9001 | Explorateur des buckets raw/clean/curated |
| **PgAdmin** | http://localhost:5050 | Interface base de données PostgreSQL |

---

## Structure du projet

```
hackaton/
├── .env                          # Variables racine (MinIO, Airflow)
├── .env.example
├── docker-compose.dev.yaml       # Stack Docker complète
│
└── apps/
    ├── api/                      # API Node.js/Express
    │   ├── src/
    │   │   ├── config/           # MinIO, Multer, Upload
    │   │   ├── controllers/      # Logique métier
    │   │   ├── middlewares/      # Auth JWT, rôles
    │   │   ├── models/           # Sequelize ORM
    │   │   └── routes/           # users, admin, documents
    │   ├── db/
    │   │   └── init.sql          # Init PostgreSQL
    │   ├── .env
    │   └── .env.example
    │
    ├── python/                   # FastAPI Python
    │   ├── main.py               # Entrée FastAPI
    │   ├── routes/               # ocr, generation
    │   ├── controllers/          # Logique OCR, SIRENE
    │   ├── ocr_traitement/       # Pipeline OCR
    │   │   ├── ocr/              # PaddleOCR
    │   │   ├── extraction/       # Détection de champs
    │   │   ├── validation/       # Alertes de conformité
    │   │   └── insee/            # Intégration API INSEE
    │   ├── .env
    │   └── .env.example
    │
    ├── web/                      # Frontend client (React/Vite)
    │   └── src/
    │       ├── pages/            # Home, Login, SignUp, Dashboard, Upload, Documents
    │       ├── components/       # Navbar, Sidebar, ...
    │       └── services/         # Clients API
    │
    ├── web-admin/                # Frontend admin (React/Vite)
    │   └── src/
    │       ├── pages/            # Dashboard, Alerts, Logs, Suppliers, ValidationDetails
    │       └── components/       # Table, StatCard, StatusBadge, ...
    │
    └── airflow/                  # Orchestration Apache Airflow
        ├── dags/
        │   └── document_pipeline.py
        └── tasks/
            ├── ingest.py
            ├── ocr.py
            ├── validate.py
            └── save_results.py
```

---

## Commandes utiles

```bash
# Voir les logs d'un service en temps réel
docker compose -f docker-compose.dev.yaml logs -f api
docker compose -f docker-compose.dev.yaml logs -f python
docker compose -f docker-compose.dev.yaml logs -f airflow-webserver

# Ouvrir un shell dans un container
docker compose -f docker-compose.dev.yaml exec api sh
docker compose -f docker-compose.dev.yaml exec python bash

# Rebuild propre (supprime les images locales)
docker compose -f docker-compose.dev.yaml down --rmi local
docker compose -f docker-compose.dev.yaml up --build
```

---

## Technologies

| Couche | Stack |
|---|---|
| Frontend | React 18, Vite, React Router |
| API backend | Node.js, Express, Sequelize, JWT, Multer |
| IA / OCR | Python 3.11, FastAPI, PaddleOCR, OpenCV |
| Base de données | PostgreSQL 15 |
| Stockage | MinIO (S3-compatible) — buckets raw / clean / curated |
| Orchestration | Apache Airflow 2 — DAG `document_pipeline` |
| Cache | Redis 7 |
| Conteneurisation | Docker, Docker Compose |

---

*© 2026 DocaTrust*
