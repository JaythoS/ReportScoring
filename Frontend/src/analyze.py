import time
from Frontend.src.mock_data import MOCK_ANALYSIS


def run_mock_analysis(file_bytes=None):
    """
    Mock analiz işlemi.
    Gerçekte LLM çağrısı burada olacak.
    Şimdilik sabit MOCK_ANALYSIS döndürür.
    """
    # Simülasyon amaçlı bekleme
    for _ in range(3):
        time.sleep(0.4)
    return MOCK_ANALYSIS


def to_dict(result):
    """
    Sonuç sözlüğünü normalize eder.
    (İleride backend’den gelen response’ları da bu formatta işleriz.)
    """
    if not isinstance(result, dict):
        return {
            "total": 0.0,
            "sections": []
        }

    # total yoksa ortalama hesapla
    if "total" not in result and "sections" in result:
        scores = [s.get("score", 0) for s in result["sections"]]
        result["total"] = round(sum(scores) / len(scores), 2) if scores else 0.0

    return {
        "total": result.get("total", 0.0),
        "sections": result.get("sections", [])
    }
