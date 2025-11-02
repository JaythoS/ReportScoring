from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import random

@dataclass
class SectionScore:
    name: str
    score: float
    evidence: str
    suggestion: str

@dataclass
class AnalysisResult:
    sections: List[SectionScore]
    total: float

RUBRIC = [
    ("Introduction", "Amaç cümlesi ve problem tanımı."),
    ("Method", "Yöntem açık, örneklem ve araçlar tanımlı."),
    ("Results", "Bulgular net, tablo/grafik uygun."),
    ("Conclusion", "Kısıtlar ve gelecek iş tanımlı.")
]

SUGGESTIONS = {
    "Introduction": "Amaç cümlesini netleştir ve kapsamı belirt.",
    "Method": "Örneklem büyüklüğü ve ölçüm araçlarını ekle.",
    "Results": "Grafiklere eksen/etiket ekle.",
    "Conclusion": "Kısıtlar ve gelecekteki çalışmalar ekle."
}

def run_mock_analysis(text: str | None) -> AnalysisResult:
    # Basit rastgele puanlayıcı (demo)
    sections = []
    total = 0.0
    for name, hint in RUBRIC:
        score = round(random.uniform(6.5, 8.5), 1)
        total += score
        evidence = f"Metinden alıntı: ... ({name})"
        suggestion = SUGGESTIONS.get(name, "Metni güçlendir.")
        sections.append(SectionScore(name=name, score=score, evidence=evidence, suggestion=suggestion))
    total = round(total / len(RUBRIC), 2)
    return AnalysisResult(sections=sections, total=total)

def to_dict(result: AnalysisResult) -> Dict[str, Any]:
    return {
        "sections": [asdict(s) for s in result.sections],
        "total": result.total
    }
