import logging
import os
import re
from typing import TypedDict

import pdfplumber

from backend.workers.extractor.utils.easyocr_fallback import extract_easyocr_text
from backend.workers.extractor.utils.render_page import render_page_to_image

logging.getLogger("pdfminer").setLevel(logging.ERROR)


class PageTextResult(TypedDict):
    page: int
    chars: int
    path: str
    text: str


def extract_text_from_pdf(
    pdf_path: str, page_number: int, output_dir: str = "tmp/output/text"
) -> PageTextResult:
    os.makedirs(output_dir, exist_ok=True)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            if page_number < 1 or page_number > total_pages:
                raise IndexError(f"Page {page_number} out of range (1–{total_pages})")

            page = pdf.pages[page_number - 1]
            text: str = page.extract_text() or ""
            text = re.sub(r"\s+", " ", text).strip()

            if len(text) < 50:
                print(f"Page {page_number}: Low or no selectable text, running OCR…")
                img_path = render_page_to_image(pdf_path, page_number)
                ocr_result = extract_easyocr_text(img_path, visualize=False)
                text = ocr_result.get("text", "").strip()

            file_path = os.path.join(output_dir, f"page_{page_number}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            return {
                "page": page_number,
                "chars": len(text),
                "path": file_path,
                "text": text,
            }

    except Exception as e:
        print(f"Failed to extract text from page {page_number}: {e}")
        return {"page": page_number, "chars": 0, "path": "", "text": ""}


def extract_text_from_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    lines = text.splitlines()
    chunks = ["\n".join(lines[i : i + 50]) for i in range(0, len(lines), 50)]
    return [
        {"page": i + 1, "text": chunk, "needs_vision": False}
        for i, chunk in enumerate(chunks)
    ]
