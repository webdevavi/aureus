import os
from pathlib import Path
import fitz  # PyMuPDF
import cv2
import numpy as np


def render_page_to_image(pdf_path: str, page_num: int, dpi: int = 96) -> str:
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = img.shape[:2]
    scale = 1024 / max(w, h)
    if scale < 1.0:
        img = cv2.resize(
            img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA
        )

    output_dir = Path("tmp/output/pages")
    output_dir.mkdir(parents=True, exist_ok=True)
    img_path = output_dir / f"{Path(pdf_path).stem}_page_{page_num}.jpg"
    cv2.imwrite(str(img_path), img_gray, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

    doc.close()
    return str(img_path)


def preprocess_for_vision(image_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path

    h, w = img.shape[:2]

    scale = 900 / max(h, w)
    if scale < 1.0:
        img = cv2.resize(
            img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA
        )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    jpeg_path = os.path.splitext(image_path)[0] + "_vision.jpg"
    cv2.imwrite(jpeg_path, gray, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return jpeg_path
