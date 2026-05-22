import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

SAMPLE_ROWS = [
    {"project": "Alpha", "status": "active",   "score": 92},
    {"project": "Beta",  "status": "inactive", "score": 45},
    {"project": "Gamma", "status": "active",   "score": None},
    {"project": "Beta",  "status": "inactive", "score": 45},  # doublon exact de la ligne 2
]


class TestHealth:
    def test_health(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestAnalyzeQuality:
    def test_analyze_returns_report(self) -> None:
        payload = {"name": "test_ds", "rows": SAMPLE_ROWS}
        resp = client.post("/api/v1/quality/analyze", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["dataset"] == "test_ds"
        assert body["total_rows"] == 4
        assert body["total_columns"] == 3
        assert 0.0 <= body["overall_score"] <= 100.0

    def test_missing_detection(self) -> None:
        resp = client.post("/api/v1/quality/analyze", json={"name": "ds", "rows": SAMPLE_ROWS})
        score_col = next(c for c in resp.json()["columns"] if c["column"] == "score")
        assert score_col["missing"] == 1
        assert score_col["missing_pct"] == 25.0

    def test_duplicate_detection(self) -> None:
        resp = client.post("/api/v1/quality/analyze", json={"name": "ds", "rows": SAMPLE_ROWS})
        assert resp.json()["duplicate_rows"] == 1

    def test_empty_rows_rejected(self) -> None:
        resp = client.post("/api/v1/quality/analyze", json={"name": "ds", "rows": []})
        assert resp.status_code == 422


class TestValidateRules:
    def test_not_null_violation(self) -> None:
        payload = {
            "name": "ds",
            "rows": SAMPLE_ROWS,
            "rules": [{"column": "score", "rule": "not_null"}],
        }
        resp = client.post("/api/v1/quality/validate", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert not body["is_valid"]
        assert body["violation_count"] == 1

    def test_regex_valid(self) -> None:
        payload = {
            "name": "ds",
            "rows": [{"email": "user@example.com"}, {"email": "bad-email"}],
            "rules": [{"column": "email", "rule": "regex", "value": r"[^@]+@[^@]+\.[^@]+"}],
        }
        resp = client.post("/api/v1/quality/validate", json=payload)
        body = resp.json()
        assert not body["is_valid"]
        assert body["violation_count"] == 1

    def test_min_rule(self) -> None:
        payload = {
            "name": "ds",
            "rows": [{"val": 10}, {"val": 5}, {"val": 0}],
            "rules": [{"column": "val", "rule": "min", "value": 6}],
        }
        resp = client.post("/api/v1/quality/validate", json=payload)
        assert resp.json()["violation_count"] == 2

    def test_unknown_column_raises_422(self) -> None:
        payload = {
            "name": "ds",
            "rows": SAMPLE_ROWS,
            "rules": [{"column": "inexistant", "rule": "not_null"}],
        }
        resp = client.post("/api/v1/quality/validate", json=payload)
        assert resp.status_code == 422

    def test_all_valid(self) -> None:
        payload = {
            "name": "ds",
            "rows": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            "rules": [
                {"column": "name", "rule": "not_null"},
                {"column": "age", "rule": "min", "value": 18},
                {"column": "age", "rule": "max", "value": 99},
            ],
        }
        resp = client.post("/api/v1/quality/validate", json=payload)
        assert resp.json()["is_valid"] is True
