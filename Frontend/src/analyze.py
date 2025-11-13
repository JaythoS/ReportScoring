# Frontend/src/analyze.py

import time
from Frontend.src.mock_data import MOCK_ANALYSIS
from Frontend.src.real_analysis import analyze_report  # az önce yazdığımız fonksiyon

USE_MOCK = False

def run_analysis(file_bytes=None, filename: str | None = None):
    """
    FE için ana entry point.
    """
    if USE_MOCK or file_bytes is None or filename is None:
        # Eski davranış: mock
        for _ in range(3):
            time.sleep(0.4)
        return MOCK_ANALYSIS

    # Gerçek analiz
    return analyze_report(file_bytes, filename)


def to_dict(result):
    """
    Sonucu normalize eder (eski to_dict aynen kalsın).
    """
    if not isinstance(result, dict):
        return {"total": 0.0, "sections": []}

    if "total" not in result and "sections" in result:
        scores = [s.get("score", 0) for s in result["sections"]]
        result["total"] = round(sum(scores) / len(scores), 2) if scores else 0.0

    return {
        "total": result.get("total", 0.0),
        "sections": result.get("sections", []),
    }


# Eski isimle uyumluluk için:
def run_mock_analysis(file_bytes=None):
    return run_analysis(file_bytes, filename=None)
