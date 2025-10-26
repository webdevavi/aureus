from typing import cast
import cv2
from rich import print
from backend.workers.extractor.utils.ocr_manager import load_easyocr


def visual_score(image_path: str):
    import cv2, numpy as np

    img = cv2.imread(image_path)
    if img is None:
        return 0.0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    edge_density = np.sum(edges > 0) / edges.size

    img_small = cv2.resize(img, (64, 64))
    data: np.ndarray = img_small.reshape((-1, 3)).astype(np.float32)

    K = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    retval, labels, centers = cv2.kmeans(
        data,
        K,
        None,  # type: ignore[arg-type]
        criteria,
        5,
        cv2.KMEANS_RANDOM_CENTERS,
    )

    color_variety = len(np.unique(labels)) / float(K)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=gray.shape[0] // 4,
        param1=50,
        param2=30,
        minRadius=50,
        maxRadius=gray.shape[0] // 2,
    )
    circle_detected = 1.0 if circles is not None else 0.0

    score = (0.35 * edge_density) + (0.4 * color_variety) + (0.25 * circle_detected)
    return float(min(score, 1.0))


def caption_score(image_path: str) -> float:
    reader = load_easyocr()
    try:
        result = reader.readtext(image_path, detail=0)
        text_list = cast(list[str], result)
        text = " ".join(text_list).lower()
    except Exception:
        return 0.0

    keywords = [
        "chart",
        "figure",
        "graph",
        "trend",
        "data",
        "as shown",
        "fy",
        "production",
        "sales",
    ]
    hits = sum(k in text for k in keywords)
    return float(min(hits / 3.0, 1.0))


def analyze_page(image_path: str, visualize: bool = False) -> dict:
    v_score = visual_score(image_path)
    c_score = caption_score(image_path)
    combined = 0.7 * v_score + 0.3 * c_score

    reader = load_easyocr()
    try:
        text_blocks = reader.readtext(image_path, detail=0)
        text_blocks = cast(list[str], text_blocks)
        text_str = " ".join(text_blocks).lower()
        word_count = len(text_str.split())
    except Exception:
        word_count = 0
        text_str = ""

    has_exclusion_terms = any(
        t in text_str
        for t in ["thank you", "disclaimer", "appendix", "contents", "notes"]
    )

    if has_exclusion_terms or word_count > 300 or v_score < 0.2:
        label = "text_only"
    elif v_score > 0.7 and word_count < 120:
        label = "chart_present"
    elif 0.55 < combined <= 0.7 and word_count < 200:
        label = "mixed"
    elif 0.35 < v_score < 0.6 and 80 < word_count < 300:
        label = "table_only"
    else:
        label = "text_only"

    print(
        f"[cyan]Page analysis:[/cyan] visual={v_score:.2f}, caption={c_score:.2f}, "
        f"words={word_count}, → [yellow]{label}[/yellow]"
    )

    if visualize:
        img = cv2.imread(image_path)
        h, w = img.shape[:2]  # type: ignore
        cv2.putText(  # type: ignore
            img,  # type: ignore
            f"{label} ({combined:.2f})",
            (30, h - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        vis_path = image_path.replace(".png", "_analyzed.png")
        cv2.imwrite(vis_path, img)  # type: ignore
        print(f"[dim]Visualization saved to {vis_path}[/dim]")

    return {
        "type": label,
        "visual_score": v_score,
        "caption_score": c_score,
        "word_count": word_count,
    }


def extract_chart_region(image_path: str, min_area_ratio: float = 0.1):
    import cv2, numpy as np, os

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # type: ignore
    edges = cv2.Canny(gray, 80, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = gray.shape

    # pick the biggest reasonably large contour
    candidates = [cv2.boundingRect(c) for c in contours]
    candidates = [r for r in candidates if (r[2] * r[3]) / (w * h) > min_area_ratio]
    if not candidates:
        return None

    x, y, cw, ch = max(candidates, key=lambda r: r[2] * r[3])
    crop = img[y : y + ch, x : x + cw]  # type: ignore

    crop_path = os.path.splitext(image_path)[0] + "_chart_crop.png"
    cv2.imwrite(crop_path, crop)
    return crop_path
