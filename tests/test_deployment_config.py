from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

import app

ROOT = Path(__file__).resolve().parents[1]


def run_api_module(expression: str) -> str:
    script = f"import {{ normalizeApiBaseUrl }} from './src/api.js'; console.log({expression});"
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_api_url_uses_local_fallback() -> None:
    assert run_api_module("normalizeApiBaseUrl()") == "http://127.0.0.1:8000"


def test_api_url_accepts_environment_value_and_normalizes_slashes() -> None:
    assert run_api_module("normalizeApiBaseUrl('https://api.example.test///')") == "https://api.example.test"
    source = (ROOT / "src" / "api.js").read_text(encoding="utf-8")
    assert "import.meta.env?.VITE_API_BASE_URL" in source


def test_cors_origins_are_configurable_and_keep_local_development(monkeypatch) -> None:
    monkeypatch.setenv(
        "FRONTEND_ORIGINS",
        " https://site.example.test/,https://outro.example.test ",
    )
    origins = app.parse_frontend_origins()
    assert "https://site.example.test" in origins
    assert "https://outro.example.test" in origins
    assert set(app.LOCAL_FRONTEND_ORIGINS) <= set(origins)


def test_cors_rejects_wildcard_with_credentials() -> None:
    try:
        app.parse_frontend_origins("*")
    except ValueError as error:
        assert "não pode conter '*'" in str(error)
    else:
        raise AssertionError("CORS aceitou origem curinga")


def test_netlify_configuration_builds_vite_and_has_spa_fallback() -> None:
    config = tomllib.loads((ROOT / "netlify.toml").read_text(encoding="utf-8"))
    assert config["build"]["command"] == "npm run build"
    assert config["build"]["publish"] == "dist"
    assert config["build"]["environment"]["NODE_VERSION"] == "22"
    assert config["redirects"][-1] == {"from": "/*", "to": "/index.html", "status": 200}


def test_render_configuration_runs_fastapi_and_checks_health() -> None:
    config = (ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "branch: main" in config
    assert "buildCommand: pip install -r requirements.txt" in config
    assert "startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT" in config
    assert "healthCheckPath: /api/health" in config
    assert "value: 3.13.5" in config


def test_health_check_reports_matrix_validation() -> None:
    payload = app.health()
    assert payload == {"ok": not app.MATRIX_ERRORS, "errors": app.MATRIX_ERRORS}


def test_protected_mathematical_and_published_data_are_unchanged() -> None:
    scoring = (ROOT / "scoring.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(scoring).hexdigest() == "8d40d85428646c8f80dce63ffc8d7e244f5600cab4df8d93247449280a04c81d"

    questions = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
    question_contract = [
        {"id": item["id"], "theme": item["theme"], "option_ids": [option["id"] for option in item["options"]]}
        for item in questions
    ]
    assert hashlib.sha256(json.dumps(question_contract, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == "e5a68e446535a55998cfa2cceee3fa974c326bf4e8b983f32c338ef50f47c756"

    candidates = json.loads((ROOT / "data/candidates.json").read_text(encoding="utf-8"))
    protected_candidate_data = [{key: value for key, value in item.items() if key != "social_links"} for item in candidates]
    assert hashlib.sha256(json.dumps(protected_candidate_data, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == "d39ffbc8faaf66400ea4df5d469bcc759a3f8d9dcf39b696f9100d9d4545c687"


def test_environment_examples_and_deploy_files_contain_no_secrets() -> None:
    env_lines = (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    values = dict(line.split("=", 1) for line in env_lines if line and not line.startswith("#"))
    assert values["VITE_API_BASE_URL"] == "http://127.0.0.1:8000"
    assert "FRONTEND_ORIGINS" in values

    versioned_config = "\n".join(
        (ROOT / filename).read_text(encoding="utf-8")
        for filename in (".env.example", "netlify.toml", "render.yaml")
    ).lower()
    assert "api_key=ai" not in versioned_config
    assert "secret=" not in versioned_config


def test_real_environment_files_remain_ignored() -> None:
    result = subprocess.run(
        ["git", "check-ignore", ".env", ".env.production"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert set(result.stdout.splitlines()) == {".env", ".env.production"}
