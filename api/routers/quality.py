import re
from io import StringIO

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, status

from api.schemas import (
    DatasetPayload,
    QualityReport,
    ColumnReport,
    ValidationPayload,
    ValidationReport,
    ValidationViolation,
)

router = APIRouter()


def _build_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _compute_quality_report(name: str, df: pd.DataFrame) -> QualityReport:
    total_rows, total_columns = df.shape
    complete_rows = int(df.dropna().shape[0])
    duplicate_rows = int(df.duplicated().sum())

    columns: list[ColumnReport] = []
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        unique = int(series.nunique(dropna=True))
        col_report = ColumnReport(
            column=col,
            dtype=str(series.dtype),
            total=total_rows,
            missing=missing,
            missing_pct=round(missing / total_rows * 100, 2),
            unique=unique,
            unique_pct=round(unique / total_rows * 100, 2),
        )
        if pd.api.types.is_numeric_dtype(series):
            col_report.min = float(series.min(skipna=True))
            col_report.max = float(series.max(skipna=True))
            col_report.mean = round(float(series.mean(skipna=True)), 4)
            col_report.std = round(float(series.std(skipna=True)), 4)
        columns.append(col_report)

    # Score : pénalise les valeurs manquantes et les doublons
    missing_rate = 1 - (df.isna().sum().sum() / (total_rows * total_columns)) if total_columns > 0 else 1.0
    dup_rate = 1 - (duplicate_rows / total_rows)
    overall_score = round((missing_rate * 0.7 + dup_rate * 0.3) * 100, 2)

    return QualityReport(
        dataset=name,
        total_rows=total_rows,
        total_columns=total_columns,
        complete_rows=complete_rows,
        complete_rows_pct=round(complete_rows / total_rows * 100, 2),
        duplicate_rows=duplicate_rows,
        duplicate_rows_pct=round(duplicate_rows / total_rows * 100, 2),
        overall_score=overall_score,
        columns=columns,
    )


@router.post(
    "/quality/analyze",
    response_model=QualityReport,
    status_code=status.HTTP_200_OK,
    summary="Analyser la qualité d'un dataset JSON",
)
async def analyze_quality(payload: DatasetPayload) -> QualityReport:
    """
    Analyse la qualité d'un dataset fourni en JSON.

    Calcule pour chaque colonne :
    - taux de valeurs manquantes
    - cardinalité (valeurs uniques)
    - statistiques descriptives (numériques)

    Retourne un **score qualité global** de 0 à 100.
    """
    try:
        df = _build_dataframe(payload.rows)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _compute_quality_report(payload.name, df)


@router.post(
    "/quality/analyze/csv",
    response_model=QualityReport,
    status_code=status.HTTP_200_OK,
    summary="Analyser la qualité d'un fichier CSV uploadé",
)
async def analyze_quality_csv(
    file: UploadFile = File(..., description="Fichier CSV à analyser"),
    name: str = "uploaded_dataset",
) -> QualityReport:
    """
    Upload un fichier CSV et retourne le rapport de qualité.

    Accepte les fichiers `.csv` uniquement (max 10 MB recommandé).
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Seuls les fichiers CSV sont acceptés",
        )
    content = await file.read()
    try:
        df = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _compute_quality_report(name or file.filename, df)


@router.post(
    "/quality/validate",
    response_model=ValidationReport,
    status_code=status.HTTP_200_OK,
    summary="Valider des règles métier sur un dataset",
)
async def validate_rules(payload: ValidationPayload) -> ValidationReport:
    """
    Valide des règles métier sur un dataset.

    **Règles supportées :**
    | Règle | Description | `value` |
    |-------|-------------|---------|
    | `not_null` | La colonne ne doit pas avoir de valeurs nulles | — |
    | `unique` | Les valeurs de la colonne doivent être uniques | — |
    | `min` | La valeur numérique doit être ≥ `value` | nombre |
    | `max` | La valeur numérique doit être ≤ `value` | nombre |
    | `regex` | La valeur doit correspondre au pattern `value` | pattern |
    """
    try:
        df = _build_dataframe(payload.rows)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    violations: list[ValidationViolation] = []

    for rule in payload.rules:
        col = rule.column
        if col not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Colonne introuvable : '{col}'",
            )

        for idx, val in enumerate(df[col]):
            violation: ValidationViolation | None = None

            if rule.rule == "not_null" and (val is None or (isinstance(val, float) and pd.isna(val))):
                violation = ValidationViolation(
                    row_index=idx, column=col, rule=rule.rule, value=val,
                    message=f"Valeur nulle interdite sur '{col}'",
                )

            elif rule.rule == "unique":
                if df[col].tolist().count(val) > 1:
                    violation = ValidationViolation(
                        row_index=idx, column=col, rule=rule.rule, value=val,
                        message=f"Valeur dupliquée sur '{col}' : {val!r}",
                    )

            elif rule.rule == "min" and rule.value is not None:
                try:
                    if float(val) < float(rule.value):
                        violation = ValidationViolation(
                            row_index=idx, column=col, rule=rule.rule, value=val,
                            message=f"Valeur {val} inférieure au minimum {rule.value}",
                        )
                except (TypeError, ValueError):
                    pass

            elif rule.rule == "max" and rule.value is not None:
                try:
                    if float(val) > float(rule.value):
                        violation = ValidationViolation(
                            row_index=idx, column=col, rule=rule.rule, value=val,
                            message=f"Valeur {val} supérieure au maximum {rule.value}",
                        )
                except (TypeError, ValueError):
                    pass

            elif rule.rule == "regex" and rule.value is not None:
                if val is None or not re.fullmatch(str(rule.value), str(val)):
                    violation = ValidationViolation(
                        row_index=idx, column=col, rule=rule.rule, value=val,
                        message=f"Valeur {val!r} ne correspond pas au pattern '{rule.value}'",
                    )

            if violation:
                violations.append(violation)

    return ValidationReport(
        dataset=payload.name,
        total_rows=len(payload.rows),
        violations=violations,
        is_valid=len(violations) == 0,
        violation_count=len(violations),
    )


@router.get(
    "/quality/rules",
    summary="Lister les règles de validation disponibles",
)
async def list_rules() -> dict[str, list[dict[str, str]]]:
    """Retourne la liste des règles de validation supportées et leur description."""
    return {
        "rules": [
            {"name": "not_null", "description": "La valeur ne doit pas être nulle", "value": "non requis"},
            {"name": "unique", "description": "Les valeurs doivent être uniques dans la colonne", "value": "non requis"},
            {"name": "min", "description": "La valeur numérique doit être >= value", "value": "nombre"},
            {"name": "max", "description": "La valeur numérique doit être <= value", "value": "nombre"},
            {"name": "regex", "description": "La valeur doit correspondre au pattern regex", "value": "pattern regex"},
        ]
    }
