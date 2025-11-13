#!/usr/bin/env python3
"""
Tam Pipeline Scripti

Bu script, PDF veya metin dosyasını alarak aşağıdaki adımları orkestre eder:

1. Metin çıkarımı (PDF ise)
2. Metni kaydetme (`data/processed/texts/`)
3. Anonimleştirme (`scripts/anonymize.py` modülünü kullanarak)
4. (Opsiyonel) Segmentasyon (LLM entegrasyonu - isteğe bağlı)

Not: Segmentasyon adımı Gemini API anahtarı gerektirdiği için varsayılan olarak
devre dışıdır. `--run-segmentation` bayrağı ile etkinleştirilebilir.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from typing import Optional

# Proje kökünü path'e ekle
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def log(msg: str) -> None:
    """Basit logger"""
    print(msg)


def safe_report_id(name: str) -> str:
    """Dosya adından güvenli report_id oluştur (report_xxx formatı)."""
    stem = Path(name).stem

    # Eğer zaten report_XXX formatındaysa
    if stem.startswith("report_") and len(stem) >= 11 and stem[7:10].isdigit():
        return stem[:11]

    # Harf/digit dışı karakterleri temizle
    cleaned = ''.join(c if c.isalnum() else '_' for c in stem)
    if len(cleaned) >= 3:
        return f"report_{cleaned[:3].zfill(3)}"
    return "report_000"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """PDF'den metin çıkar (llm.tools.pdf_extractor'ı kullanarak)."""
    from llm.tools.pdf_extractor import extract_text

    return extract_text(str(pdf_path))


def save_text(report_id: str, text: str) -> Path:
    """Metni `data/processed/texts/` klasörüne kaydet."""
    output_dir = PROJECT_ROOT / "data" / "processed" / "texts"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{report_id}.txt"
    output_path.write_text(text, encoding="utf-8")
    return output_path


def run_anonymization(text_path: Path, report_id: str, save_mapping: bool = True) -> dict:
    """Metni anonimleştir ve sonuç dosyalarını döndür."""
    from scripts.anonymize import anonymize_file

    anonymized_dir = PROJECT_ROOT / "data" / "processed" / "anonymized"
    anonymized_dir.mkdir(parents=True, exist_ok=True)
    anonymized_path = anonymized_dir / f"{report_id}_anonymized.txt"

    mapping_path = None
    if save_mapping:
        mapping_dir = PROJECT_ROOT / "data" / "processed" / "anonymization_mappings"
        mapping_dir.mkdir(parents=True, exist_ok=True)
        mapping_path = mapping_dir / f"{report_id}_mapping.json"

    mapping_dict = anonymize_file(
        input_path=text_path,
        output_path=anonymized_path,
        mapping_path=mapping_path,
        report_id=report_id,
    )

    return {
        "anonymized_text": anonymized_path,
        "mapping_file": mapping_path,
        "mapping": mapping_dict,
    }


def run_segmentation(text: str, report_id: str) -> Optional[Path]:
    """Metni segment et (Gemini chunked). Başarılıysa segmentation dosya yolu döndür."""
    try:
        from llm.tools.gemini_segment_chunked import segment_text_chunked
        from llm.tools.fix_segmentation import fix_segmentation
        from llm.tools.validate_segmentation import validate_segmentation
        from llm.tools.validate_segmentation import print_validation_report
    except ImportError:
        log("  Segmentasyon modülleri yüklenemedi. Bu adım atlanacak.")
        return None

    log("🔍 Segmentasyon başlatılıyor...")
    try:
        result_json = segment_text_chunked(text)
    except Exception as exc:
        log(f" Segmentasyon başarısız: {exc}")
        return None

    segmentation_dir = PROJECT_ROOT / "data" / "processed" / "segmentations"
    segmentation_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    segmentation_path = segmentation_dir / f"{report_id}_segmentation_{timestamp}.json"
    segmentation_path.write_text(result_json, encoding="utf-8")
    log(f" Segmentasyon çıktısı kaydedildi: {segmentation_path}")

    # Fix segmentation
    try:
        fixed_data = fix_segmentation(segmentation_path, text)
        fixed_path = segmentation_path.with_suffix('.fixed.json')
        fixed_path.write_text(json.dumps(fixed_data, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f" Düzeltilmiş segmentasyon: {fixed_path}")

        validation_result = validate_segmentation(fixed_path)
        print_validation_report(validation_result)
    except Exception as exc:
        log(f"  Segmentasyon düzeltme/validasyon hatası: {exc}")

    return segmentation_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Tam pipeline çalıştır (metin çıkarımı, anonimleştirme, segmentasyon)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", type=str, help="Girdi PDF dosyası")
    group.add_argument("--text", type=str, help="Girdi metin dosyası (önceden çıkarılmış)")

    parser.add_argument("--report-id", type=str, help="Opsiyonel rapor ID'si (report_XXX)")
    parser.add_argument("--skip-segmentation", action="store_true", help="Segmentasyon adımını atla")
    parser.add_argument("--skip-anonymization", action="store_true", help="Anonimleştirme adımını atla")
    parser.add_argument("--no-mapping", action="store_true", help="Mapping dosyası oluşturma")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve() if args.pdf else None
    text_path = Path(args.text).resolve() if args.text else None

    if pdf_path and not pdf_path.exists():
        log(f" PDF dosyası bulunamadı: {pdf_path}")
        sys.exit(1)
    if text_path and not text_path.exists():
        log(f" Metin dosyası bulunamadı: {text_path}")
        sys.exit(1)

    report_id = args.report_id
    if not report_id:
        if pdf_path:
            report_id = safe_report_id(pdf_path.name)
        else:
            report_id = safe_report_id(text_path.name)

    log("=" * 70)
    log("TAM PIPELINE")
    log("=" * 70)
    log(f" Rapor ID: {report_id}")
    if pdf_path:
        log(f" PDF: {pdf_path}")
    if text_path:
        log(f" Metin: {text_path}")
    log("")

    # 1) Metin çıkarımı
    extracted_text = None
    saved_text_path = None

    if pdf_path:
        log(" PDF metin çıkarımı yapılıyor...")
        try:
            extracted_text = extract_text_from_pdf(pdf_path)
            log(f" Metin çıkarıldı: {len(extracted_text):,} karakter")
        except Exception as exc:
            log(f" Metin çıkarma hatası: {exc}")
            sys.exit(1)
    else:
        extracted_text = text_path.read_text(encoding="utf-8")

    # 2) Metni kaydet
    saved_text_path = save_text(report_id, extracted_text)
    log(f" Metin kaydedildi: {saved_text_path}")

    # 3) Anonimleştirme
    anonymization_result = None
    if not args.skip_anonymization:
        log(" Anonimleştirme çalıştırılıyor...")
        anonymization_result = run_anonymization(
            text_path=saved_text_path,
            report_id=report_id,
            save_mapping=not args.no_mapping,
        )
        log(f" Anonimleştirilmiş metin: {anonymization_result['anonymized_text']}")
        if anonymization_result["mapping_file"]:
            log(f" Mapping dosyası: {anonymization_result['mapping_file']}")

    # 4) Segmentasyon (opsiyonel)
    if args.skip_segmentation:
        log("  Segmentasyon adımı kullanıcı isteğiyle atlandı.")
    else:
        segmentation_path = run_segmentation(extracted_text, report_id)
        if segmentation_path:
            log(f" Segmentasyon çıktısı: {segmentation_path}")

    log("")
    log(" Pipeline tamamlandı!")

    # Özet
    summary = {
        "report_id": report_id,
        "text_file": str(saved_text_path),
        "anonymized_text": str(anonymization_result["anonymized_text"]) if anonymization_result else None,
        "mapping_file": str(anonymization_result["mapping_file"]) if anonymization_result and anonymization_result["mapping_file"] else None,
    }
    log(" Özet:")
    for key, value in summary.items():
        log(f"   {key}: {value}")


if __name__ == "__main__":
    main()
