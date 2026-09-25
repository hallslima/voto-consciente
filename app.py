from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scoring import NO_OPINION, calculate_results
from validation import validate_matrix

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOCAL_FRONTEND_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
)


def parse_frontend_origins(value: str | None = None) -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "") if value is None else value
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("FRONTEND_ORIGINS não pode conter '*' quando credenciais estão habilitadas")
    return list(dict.fromkeys((*LOCAL_FRONTEND_ORIGINS, *origins)))


def load_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


QUESTIONS = load_json("questions.json")
CANDIDATES = [
    candidate
    for candidate in load_json("candidates.json")
    if candidate.get("registration_status") == "Deferido"
]
RESEARCH_EVIDENCE = load_json("research_evidence.json")
MATRIX_ERRORS = validate_matrix(QUESTIONS, CANDIDATES)


class QuestionnairePayload(BaseModel):
    answers: dict[str, str]
    weights: dict[str, int] = Field(default_factory=dict)


app = FastAPI(title="Voto Consciente Pernambuco API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": not MATRIX_ERRORS, "errors": MATRIX_ERRORS}


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    if MATRIX_ERRORS:
        raise HTTPException(status_code=500, detail=MATRIX_ERRORS)
    return {"questions": QUESTIONS, "candidates": CANDIDATES, "research_evidence": RESEARCH_EVIDENCE}


@app.post("/api/results")
def results(payload: QuestionnairePayload) -> dict[str, Any]:
    if MATRIX_ERRORS:
        raise HTTPException(status_code=500, detail=MATRIX_ERRORS)

    question_ids = {question["id"] for question in QUESTIONS}
    option_ids = {
        question["id"]: {option["id"] for option in question["options"]}
        for question in QUESTIONS
    }
    unknown_answers = set(payload.answers) - question_ids
    if unknown_answers:
        raise HTTPException(status_code=400, detail="Pergunta desconhecida no questionário.")

    invalid_answers = {
        question_id
        for question_id, answer in payload.answers.items()
        if answer != NO_OPINION and answer not in option_ids[question_id]
    }
    if invalid_answers:
        raise HTTPException(status_code=400, detail="Alternativa inválida no questionário.")

    invalid_weights = {
        question_id
        for question_id, weight in payload.weights.items()
        if question_id not in question_ids or weight not in {1, 2, 3}
    }
    if invalid_weights:
        raise HTTPException(status_code=400, detail="Os pesos devem ser 1, 2 ou 3.")

    answered = [value for value in payload.answers.values() if value != NO_OPINION]
    if not answered:
        raise HTTPException(status_code=400, detail="Escolha pelo menos uma resposta.")

    calculated = calculate_results(
        QUESTIONS,
        CANDIDATES,
        payload.answers,
        payload.weights,
    )
    return {"results": [asdict(result) for result in calculated]}
