from pydantic import BaseModel, Field, field_validator
from typing import Any


class DatasetPayload(BaseModel):
    """Payload contenant un tableau de données à analyser."""

    name: str = Field(..., description="Nom du dataset")
    rows: list[dict[str, Any]] = Field(..., min_length=1, description="Lignes de données")

    @field_validator("rows")
    @classmethod
    def rows_not_empty(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not v:
            raise ValueError("Le dataset doit contenir au moins une ligne")
        return v


class ColumnReport(BaseModel):
    """Rapport de qualité pour une colonne."""

    column: str
    dtype: str
    total: int
    missing: int
    missing_pct: float
    unique: int
    unique_pct: float
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    std: float | None = None


class QualityReport(BaseModel):
    """Rapport global de qualité d'un dataset."""

    dataset: str
    total_rows: int
    total_columns: int
    complete_rows: int
    complete_rows_pct: float
    duplicate_rows: int
    duplicate_rows_pct: float
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Score qualité de 0 à 100")
    columns: list[ColumnReport]


class ValidationRule(BaseModel):
    """Règle de validation à appliquer sur une colonne."""

    column: str
    rule: str = Field(..., description="not_null | unique | min | max | regex")
    value: str | float | None = None


class ValidationPayload(BaseModel):
    """Payload pour la validation de règles métier."""

    name: str
    rows: list[dict[str, Any]] = Field(..., min_length=1)
    rules: list[ValidationRule] = Field(..., min_length=1)


class ValidationViolation(BaseModel):
    """Détail d'une violation de règle."""

    row_index: int
    column: str
    rule: str
    value: Any
    message: str


class ValidationReport(BaseModel):
    """Résultat de validation de règles."""

    dataset: str
    total_rows: int
    violations: list[ValidationViolation]
    is_valid: bool
    violation_count: int
