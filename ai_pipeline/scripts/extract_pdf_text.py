from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import shutil
import subprocess
import tempfile

from pypdf import PdfReader


EXTRACTOR_VERSION = "pdf-text-extractor-v2.0.0"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF_DIR = ROOT / "public" / "documents" / "government-plans"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "generated" / "extracted-text"
DEFAULT_MANIFEST = ROOT / "data" / "generated" / "extraction_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ocr_tools() -> tuple[str | None, str | None]:
    return shutil.which("pdftoppm") or shutil.which("pdftocairo"), shutil.which("tesseract")


def extract_page_with_ocr(pdf_path: Path, page_number: int) -> tuple[str, str | None]:
    renderer, tesseract = ocr_tools()
    if not renderer or not tesseract:
        return "", "OCR não executado: Tesseract e renderizador Poppler não estão disponíveis."

    with tempfile.TemporaryDirectory(prefix="voto-consciente-ocr-") as temp_dir:
        prefix = Path(temp_dir) / "page"
        render = subprocess.run(
            [renderer, "-f", str(page_number), "-l", str(page_number), "-r", "300", "-png", str(pdf_path), str(prefix)],
            capture_output=True,
            text=True,
            check=False,
        )
        if render.returncode != 0:
            return "", f"Falha ao renderizar página {page_number}: {render.stderr.strip()}"
        images = sorted(Path(temp_dir).glob("page*.png"))
        if not images:
            return "", f"Renderizador não produziu imagem para a página {page_number}."
        ocr = subprocess.run(
            [tesseract, str(images[0]), "stdout", "-l", "por", "--psm", "6"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if ocr.returncode != 0:
            return "", f"Falha no OCR da página {page_number}: {ocr.stderr.strip()}"
        return ocr.stdout, None


def extract_pdf(path: Path, candidate_id: str, *, use_ocr: bool = False, extracted_at: str | None = None) -> dict:
    """Extract text page by page without changing or interpreting the source PDF."""
    before_hash = sha256(path)
    warnings: list[str] = []
    pages: list[dict] = []
    read_errors: list[str] = []
    parser_warnings: list[str] = []
    handler = logging.Handler()
    handler.emit = lambda record: parser_warnings.append(record.getMessage())
    pypdf_logger = logging.getLogger("pypdf")
    pypdf_logger.addHandler(handler)
    renderer, tesseract = ocr_tools()

    try:
        reader = PdfReader(str(path))
        for index, page in enumerate(reader.pages, start=1):
            method = "pypdf"
            try:
                text = page.extract_text() or ""
            except Exception as exc:  # pragma: no cover - depends on malformed external PDFs
                text = ""
                read_errors.append(f"Página {index}: {type(exc).__name__}: {exc}")
            if not text.strip() and use_ocr and renderer and tesseract:
                ocr_text, ocr_error = extract_page_with_ocr(path, index)
                if ocr_text.strip():
                    text = ocr_text
                    method = "ocr-tesseract"
                elif ocr_error:
                    read_errors.append(ocr_error)
            pages.append({"page_number": index, "text": text, "extraction_method": method})
    except Exception as exc:
        read_errors.append(f"Documento: {type(exc).__name__}: {exc}")
    finally:
        pypdf_logger.removeHandler(handler)

    text_pages = sum(bool(page["text"].strip()) for page in pages)
    character_count = sum(len(page["text"]) for page in pages)
    requires_ocr = bool(pages) and text_pages == 0
    if requires_ocr:
        warnings.append("Nenhuma página possui camada textual extraível; OCR local é necessário.")
        if use_ocr and (not renderer or not tesseract):
            warnings.append("OCR solicitado, mas não executado: Tesseract e renderizador Poppler não estão disponíveis.")
    warnings.extend(dict.fromkeys(parser_warnings))
    if read_errors:
        warnings.extend(read_errors)

    after_hash = sha256(path)
    if before_hash != after_hash:
        raise RuntimeError(f"O PDF original foi modificado durante a extração: {path}")

    return {
        "candidate_id": candidate_id,
        "source_file": path.name,
        "source_path": path.relative_to(ROOT).as_posix(),
        "source_sha256": before_hash,
        "page_count": len(pages),
        "text_page_count": text_pages,
        "character_count": character_count,
        "extractor_version": EXTRACTOR_VERSION,
        "extracted_at": extracted_at or utc_now(),
        "requires_ocr": requires_ocr,
        "original_pdf_unchanged": True,
        "pages": pages,
        "warnings": warnings,
    }


def candidate_documents(candidates_path: Path) -> list[tuple[str, Path]]:
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    return [(candidate["id"], DEFAULT_PDF_DIR / candidate["plan_document"]) for candidate in candidates]


def extract_all(candidates_path: Path, output_dir: Path, manifest_path: Path, *, use_ocr: bool = False) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_at = utc_now()
    documents = []
    for candidate_id, pdf_path in candidate_documents(candidates_path):
        if not pdf_path.is_file():
            raise FileNotFoundError(f"PDF não encontrado para {candidate_id}: {pdf_path}")
        result = extract_pdf(pdf_path, candidate_id, use_ocr=use_ocr, extracted_at=run_at)
        output_path = output_dir / f"{candidate_id}.json"
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        methods = sorted({page["extraction_method"] for page in result["pages"]})
        documents.append({
            "candidate_id": candidate_id,
            "source_file": result["source_file"],
            "source_path": result["source_path"],
            "source_sha256": result["source_sha256"],
            "page_count": result["page_count"],
            "text_page_count": result["text_page_count"],
            "character_count": result["character_count"],
            "methods": methods,
            "requires_ocr": result["requires_ocr"],
            "warnings": result["warnings"],
            "status": "requires_ocr" if result["requires_ocr"] else ("complete" if not result["warnings"] else "complete_with_warnings"),
            "output_file": output_path.relative_to(ROOT).as_posix(),
            "original_pdf_unchanged": result["original_pdf_unchanged"],
        })
    manifest = {
        "extractor_version": EXTRACTOR_VERSION,
        "extracted_at": run_at,
        "document_count": len(documents),
        "ocr_requested": use_ocr,
        "ocr_tools": {"renderer": ocr_tools()[0], "tesseract": ocr_tools()[1]},
        "documents": documents,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Extração reproduzível de texto por página, sem análise política.")
    parser.add_argument("pdf", nargs="?", type=Path, help="PDF individual (modo legado)")
    parser.add_argument("--candidate-id", help="ID obrigatório no modo de PDF individual")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--all", action="store_true", help="Processa os oito planos associados em candidates.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--ocr", action="store_true", help="Tenta OCR local em páginas sem texto, se as ferramentas existirem")
    args = parser.parse_args()

    if args.all:
        manifest = extract_all(ROOT / "data" / "candidates.json", args.output_dir, args.manifest, use_ocr=args.ocr)
        print(f"OK: {manifest['document_count']} documento(s) processado(s).")
        return
    if not args.pdf or not args.candidate_id:
        parser.error("informe --all ou um PDF com --candidate-id")
    result = extract_pdf(args.pdf, args.candidate_id, use_ocr=args.ocr)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
