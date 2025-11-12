#!/usr/bin/env python3
"""
Cover bölümünü notlandırma scripti.
PDF dosyasını segment eder ve cover bölümünü rubrik kriterlerine göre puanlar.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.scoring.common import (
    get_safe_filename,
    find_pdf_file,
    extract_and_segment_pdf,
    save_score_result
)
from src.analyze.segment_scoring import find_cover_segment, score_cover_segment


def print_cover_score_details(score_result: dict):
    """Cover skorlama detaylarını yazdır"""
    print(f"✅ Skorlama tamamlandı!")
    print(f"   📊 Toplam Puan: {score_result.get('score', 0.0):.2f}/10")
    criteria = score_result.get('criteria', {})
    print(f"   - Başlık Doğruluğu: {criteria.get('title_accuracy', 0.0):.2f}/10")
    print(f"   - Biçim: {criteria.get('format', 0.0):.2f}/10")
    print(f"   - Bilgi Tamlığı: {criteria.get('completeness', 0.0):.2f}/10")
    print(f"   - Tarih/İsim Varlığı: {criteria.get('date_name_presence', 0.0):.2f}/10")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="PDF dosyasını segment et ve cover bölümünü notlandır"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="PDF dosya adı (data/sample_reports klasöründen) veya tam yol"
    )
    args = parser.parse_args()
    
    # PDF dosyasını bul
    pdf_file = find_pdf_file(args.pdf)
    
    if not pdf_file.exists():
        print(f"❌ PDF dosyası bulunamadı: {pdf_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("COVER BÖLÜMÜ NOTLANDIRMA")
    print("=" * 70)
    print()
    print(f"📄 Rapor: {pdf_file.name}")
    print()
    
    try:
        # PDF'yi işle ve segmentasyon yap
        fixed_data, fixed_file, text = extract_and_segment_pdf(pdf_file)
        
        # Cover segmentini bul
        print("🔍 Cover segmenti aranıyor...")
        print()
        cover_segment = find_cover_segment(fixed_data)
        
        if not cover_segment:
            print("❌ Cover segmenti bulunamadı!")
            sys.exit(1)
        
        print(f"✅ Cover segmenti bulundu:")
        print(f"   - Section ID: {cover_segment.get('section_id', 'unknown')}")
        print(f"   - Section Name: {cover_segment.get('section_name', 'unknown')}")
        print(f"   - Content uzunluğu: {len(cover_segment.get('content', ''))} karakter")
        print()
        
        # Cover'ı skorla
        print("📊 Cover skorlanıyor...")
        print()
        score_result = score_cover_segment(cover_segment)
        
        # Skorlama detaylarını yazdır
        print_cover_score_details(score_result)
        
        # Sonuçları kaydet
        safe_name = get_safe_filename(pdf_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result_file = save_score_result(
            pdf_file=pdf_file,
            segmentation_file=fixed_file,
            segment=cover_segment,
            score_result=score_result,
            output_prefix="cover",
            timestamp=timestamp
        )
        
        print(f"✅ Sonuçlar JSON olarak kaydedildi: {result_file.name}")
        print(f"📁 Tam yol: {result_file}")
        print()
        print("=" * 70)
        print("İŞLEM TAMAMLANDI!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

