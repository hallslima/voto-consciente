from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

from pdf2image import convert_from_path
from pypdf import PdfReader
import pytesseract


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "public" / "documents" / "government-plans" / "raquel-lyra-55.pdf"
OUTPUT = ROOT / "data" / "generated" / "extracted-text" / "raquel_lyra.json"
MANIFEST = ROOT / "data" / "generated" / "extraction_manifest.json"
TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
POPPLER = Path(
    r"C:\Users\halli\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin"
)
LANGUAGE = "por"
DPI = 300
METHOD = "ocr-tesseract-por"
REVIEW_THRESHOLD = 50


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version_line(command: list[str]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    output = completed.stdout.strip() or completed.stderr.strip()
    return output.splitlines()[0] if output else "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR controlado do plano de Raquel Lyra.")
    parser.add_argument("--tesseract", type=Path, default=TESSERACT)
    parser.add_argument("--poppler", type=Path, default=POPPLER)
    args = parser.parse_args()

    before_hash = sha256(PDF)
    page_count = len(PdfReader(str(PDF)).pages)
    if page_count != 106:
        raise RuntimeError(f"Esperadas 106 páginas físicas; encontradas {page_count}.")
    if not args.tesseract.is_file():
        raise FileNotFoundError(f"Tesseract não encontrado: {args.tesseract}")
    pdfinfo = args.poppler / "pdfinfo.exe"
    if not pdfinfo.is_file():
        raise FileNotFoundError(f"Poppler não encontrado: {args.poppler}")

    pytesseract.pytesseract.tesseract_cmd = str(args.tesseract)
    tesseract_version = version_line([str(args.tesseract), "--version"])
    poppler_version = version_line([str(pdfinfo), "-v"])
    run_started = time.perf_counter()
    extracted_at = utc_now()
    pages = []
    run_warnings = []

    for page_number in range(1, page_count + 1):
        page_started = time.perf_counter()
        page_warnings = []
        text = ""
        try:
            image = convert_from_path(
                PDF,
                dpi=DPI,
                first_page=page_number,
                last_page=page_number,
                poppler_path=args.poppler,
                fmt="png",
                thread_count=1,
            )[0]
            text = pytesseract.image_to_string(image, lang=LANGUAGE, config="--psm 6")
        except Exception as exc:  # source/tool dependent
            message = f"Página {page_number}: {type(exc).__name__}: {exc}"
            page_warnings.append(message)
            run_warnings.append(message)

        character_count = len(text)
        manual_review = character_count < REVIEW_THRESHOLD
        pages.append(
            {
                "page_number": page_number,
                "text": text,
                "extraction_method": METHOD,
                "language": LANGUAGE,
                "dpi": DPI,
                "character_count": character_count,
                "duration_seconds": round(time.perf_counter() - page_started, 3),
                "quality": "low-extraction-review" if manual_review else "text-extracted",
                "manual_review_required": manual_review,
                "warnings": page_warnings,
            }
        )
        print(f"Página {page_number:03d}/106: {character_count} caracteres", flush=True)

    duration = round(time.perf_counter() - run_started, 3)
    after_hash = sha256(PDF)
    if before_hash != after_hash:
        raise RuntimeError("O hash do PDF original mudou durante o OCR.")

    text_pages = [page["page_number"] for page in pages if page["text"].strip()]
    empty_pages = [page["page_number"] for page in pages if not page["text"].strip()]
    review_pages = [page["page_number"] for page in pages if page["manual_review_required"]]
    total_characters = sum(page["character_count"] for page in pages)
    result = {
        "candidate_id": "raquel_lyra",
        "source_file": PDF.name,
        "source_path": PDF.relative_to(ROOT).as_posix(),
        "source_sha256": before_hash,
        "page_count": page_count,
        "text_page_count": len(text_pages),
        "empty_page_count": len(empty_pages),
        "empty_pages": empty_pages,
        "empty_or_graphic_pages": review_pages,
        "manual_review_page_count": len(review_pages),
        "manual_review_pages": review_pages,
        "character_count": total_characters,
        "extraction_method": METHOD,
        "language": LANGUAGE,
        "dpi": DPI,
        "tesseract_version": tesseract_version,
        "poppler_version": poppler_version,
        "duration_seconds": duration,
        "extracted_at": extracted_at,
        "requires_ocr": False,
        "original_pdf_unchanged": True,
        "warnings": run_warnings,
        "pages": pages,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["extracted_at"] = extracted_at
    manifest["ocr_requested"] = True
    manifest["ocr_tools"] = {
        "renderer": str(args.poppler),
        "tesseract": str(args.tesseract),
        "tesseract_version": tesseract_version,
        "poppler_version": poppler_version,
    }
    entry = next(item for item in manifest["documents"] if item["candidate_id"] == "raquel_lyra")
    entry.update(
        {
            "source_sha256": before_hash,
            "page_count": page_count,
            "text_page_count": len(text_pages),
            "empty_page_count": len(empty_pages),
            "empty_pages": empty_pages,
            "empty_or_graphic_pages": review_pages,
            "manual_review_page_count": len(review_pages),
            "manual_review_pages": review_pages,
            "character_count": total_characters,
            "methods": [METHOD],
            "extraction_method": METHOD,
            "language": LANGUAGE,
            "dpi": DPI,
            "tesseract_version": tesseract_version,
            "poppler_version": poppler_version,
            "duration_seconds": duration,
            "extracted_at": extracted_at,
            "requires_ocr": False,
            "warnings": run_warnings,
            "status": "complete" if not run_warnings else "complete_with_warnings",
            "original_pdf_unchanged": True,
        }
    )
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OCR concluído: {total_characters} caracteres em {duration}s.")


if __name__ == "__main__":
    main()
