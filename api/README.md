# Data Quality API

API REST construite avec **FastAPI** pour analyser et valider la qualité des données.  
Elle complète l'application Streamlit de ce dépôt en exposant les mêmes métriques via une interface HTTP programmatique.

## Fonctionnalités

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérification de l'état de l'API |
| `/api/v1/quality/analyze` | POST | Analyse qualité d'un dataset JSON |
| `/api/v1/quality/analyze/csv` | POST | Analyse qualité d'un fichier CSV uploadé |
| `/api/v1/quality/validate` | POST | Validation de règles métier |
| `/api/v1/quality/rules` | GET | Liste des règles disponibles |

### Métriques calculées

- **Valeurs manquantes** — taux par colonne et global
- **Doublons** — détection des lignes dupliquées
- **Cardinalité** — nombre de valeurs uniques par colonne
- **Statistiques descriptives** — min, max, moyenne, écart-type (colonnes numériques)
- **Score qualité global** — de 0 à 100 (pondération : 70% complétude + 30% unicité)

### Règles de validation supportées

| Règle | Description | Paramètre `value` |
|-------|-------------|-------------------|
| `not_null` | Interdit les valeurs nulles | — |
| `unique` | Exige l'unicité des valeurs | — |
| `min` | Valeur numérique ≥ seuil | nombre |
| `max` | Valeur numérique ≤ seuil | nombre |
| `regex` | Correspondance à un pattern regex | pattern |

---

## Installation

### Prérequis

- Python 3.11+
- pip ou [uv](https://github.com/astral-sh/uv)

### Avec pip

```bash
cd api
pip install -r requirements.txt
```

### Avec uv (recommandé)

```bash
cd api
uv pip install -r requirements.txt
```

---

## Démarrage

```bash
# Depuis la racine du projet
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est disponible sur `http://localhost:8000`.  
La documentation interactive Swagger est accessible sur `http://localhost:8000/docs`.

---

## Exemples d'utilisation

### Analyser un dataset JSON

```bash
curl -X POST http://localhost:8000/api/v1/quality/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "projets",
    "rows": [
      {"projet": "Alpha", "statut": "actif", "score": 92},
      {"projet": "Beta",  "statut": "inactif", "score": null},
      {"projet": "Alpha", "statut": "actif", "score": 92}
    ]
  }'
```

**Réponse (extrait) :**

```json
{
  "dataset": "projets",
  "total_rows": 3,
  "total_columns": 3,
  "duplicate_rows": 1,
  "duplicate_rows_pct": 33.33,
  "overall_score": 74.44,
  "columns": [
    {
      "column": "score",
      "dtype": "float64",
      "missing": 1,
      "missing_pct": 33.33,
      "unique": 1,
      "mean": 92.0
    }
  ]
}
```

### Uploader un fichier CSV

```bash
curl -X POST http://localhost:8000/api/v1/quality/analyze/csv \
  -F "file=@mon_dataset.csv" \
  -F "name=mon_dataset"
```

### Valider des règles métier

```bash
curl -X POST http://localhost:8000/api/v1/quality/validate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "employes",
    "rows": [
      {"email": "alice@example.com", "age": 28},
      {"email": "mauvais-email",     "age": 15}
    ],
    "rules": [
      {"column": "email", "rule": "regex",    "value": "[^@]+@[^@]+\\.[^@]+"},
      {"column": "age",   "rule": "min",      "value": 18},
      {"column": "email", "rule": "not_null"}
    ]
  }'
```

**Réponse :**

```json
{
  "dataset": "employes",
  "total_rows": 2,
  "is_valid": false,
  "violation_count": 2,
  "violations": [
    {"row_index": 1, "column": "email", "rule": "regex",  "message": "Valeur 'mauvais-email' ne correspond pas au pattern '...'"},
    {"row_index": 1, "column": "age",   "rule": "min",    "message": "Valeur 15 inférieure au minimum 18"}
  ]
}
```

---

## Tests

```bash
# Depuis la racine du projet
pip install pytest httpx
pytest api/tests/ -v
```

---

## Structure du projet

```
api/
├── __init__.py
├── main.py          # Application FastAPI, CORS, routeurs
├── schemas.py       # Modèles Pydantic (requêtes et réponses)
├── requirements.txt # Dépendances Python
├── routers/
│   ├── __init__.py
│   └── quality.py   # Endpoints /quality/*
└── tests/
    ├── __init__.py
    └── test_quality.py
```

---

## Architecture

```
Client HTTP
    │
    ▼
FastAPI (api/main.py)
    │
    ├── GET  /health
    └── Router /api/v1 (api/routers/quality.py)
            ├── POST /quality/analyze       → pandas DataFrame analysis
            ├── POST /quality/analyze/csv   → CSV upload → DataFrame
            ├── POST /quality/validate      → règles métier
            └── GET  /quality/rules         → catalogue des règles
```

---

## Lien avec l'application Streamlit

L'API et l'application Streamlit partagent le même dépôt :

```
groupe-projets/
├── src/app.py          # Dashboard Streamlit (branch: feature/dashboard)
├── api/                # API FastAPI       (branch: feature/fastapi-data-quality)
└── requirements.txt    # Dépendances Streamlit
```

Pour lancer les deux en parallèle :

```bash
# Terminal 1 — Streamlit
streamlit run src/app.py

# Terminal 2 — FastAPI
uvicorn api.main:app --reload --port 8000
```
