# Frontend/src/real_analysis.py
from dotenv import load_dotenv
load_dotenv()

import uuid
from pathlib import Path

from scripts.scoring.common import extract_and_segment_pdf
from core.extraction import extract_text_from_docx
from core.scoring.segment_scoring import (
    find_cover_segment,
    find_executive_summary_segment,
    score_cover_segment,
    score_executive_summary,
)

UPLOAD_DIR = Path("outputs") / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def analyze_report(file_bytes: bytes, filename: str) -> dict:
    ext = filename.split(".")[-1].lower()

    # 1) Kaydet
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(file_bytes)

    # 2) PDF ise full pipeline
    if ext == "pdf":
        fixed_seg_data, fixed_file, text = extract_and_segment_pdf(file_path)
    elif ext in ("docx", "doc"):
        text = extract_text_from_docx(file_path)
        fixed_seg_data = {
            "segmentation": {
                "sections": [
                    {
                        "section_id": "full_doc",
                        "section_name": "Full Document",
                        "content": text,
                        "level": 1,
                        "parent_id": None,
                    }
                ]
            }
        }
    else:
        return {"total": 0.0, "sections": []}

    # 3) Segmentleri bul
    cover_seg = find_cover_segment(fixed_seg_data)
    exec_seg = find_executive_summary_segment(fixed_seg_data)

    sections = []

    # Cover
    if cover_seg:
        c = score_cover_segment(cover_seg)
        sections.append({
            "name": "Cover Page",
            "score": c.get("score", 0),
            "evidence": c.get("feedback", ""),
            "suggestion": c.get("feedback", "")
        })

    # Exec summary
    if exec_seg:
        e = score_executive_summary(exec_seg)
        sections.append({
            "name": "Executive Summary",
            "score": e.get("score", 0),
            "evidence": e.get("feedback", ""),
            "suggestion": e.get("feedback", "")
        })

    # Total
    if sections:
        total = round(sum(s["score"] for s in sections) / len(sections), 2)
    else:
        total = 0.0

    return {"total": total, "sections": sections}
