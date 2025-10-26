import easyocr

_easyocr_cache = None


def load_easyocr(lang="en") -> easyocr.Reader:
    global _easyocr_cache
    if _easyocr_cache is None:
        print(f"Initializing EasyOCR ({lang})...")
        _easyocr_cache = easyocr.Reader([lang])
    return _easyocr_cache
