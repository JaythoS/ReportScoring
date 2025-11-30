#!/usr/bin/env python3
"""
Executive Summary bölümünü notlandırma scripti.
PDF dosyasını segment eder ve executive summary bölümünü rubrik kriterlerine göre puanlar.
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
from core.scoring import find_executive_summary_segment, score_executive_summary


def print_executive_score_details(score_result: dict):
    """Executive Summary skorlama detaylarını yazdır"""
    print(f" Skorlama tamamlandı!")
    print(f"    Toplam Puan: {score_result.get('score', 0)}/5")
    if 'rubric_score' in score_result:
        print(f"    Rubrik Puanı: {score_result.get('rubric_score', 0)}/100")
    criteria = score_result.get('criteria', {})
    print(f"   - Executive Summary (B1): {criteria.get('executive_summary_b1', 0)}/5")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="PDF dosyasını segment et ve Executive Summary bölümünü notlandır"
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
        print(f" PDF dosyası bulunamadı: {pdf_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("EXECUTIVE SUMMARY BÖLÜMÜ NOTLANDIRMA")
    print("=" * 70)
    print()
    print(f" Rapor: {pdf_file.name}")
    print()
    
    try:
        # PDF'yi işle ve segmentasyon yap
        fixed_data, fixed_file, text = extract_and_segment_pdf(pdf_file)
        
        # Executive Summary segmentini bul
        print(" Executive Summary segmenti aranıyor...")
        print()
        executive_segment = find_executive_summary_segment(fixed_data)
        
        if not executive_segment:
            print(" Executive Summary segmenti bulunamadı!")
            sys.exit(1)
        
        print(f" Executive Summary segmenti bulundu:")
        print(f"   - Section ID: {executive_segment.get('section_id', 'unknown')}")
        print(f"   - Section Name: {executive_segment.get('section_name', 'unknown')}")
        print(f"   - Content uzunluğu: {len(executive_segment.get('content', ''))} karakter")
        print()
        
        # Executive Summary'yi skorla
        print(" Executive Summary skorlanıyor...")
        print()
        score_result = score_executive_summary(executive_segment)
        
        # Skorlama detaylarını yazdır
        print_executive_score_details(score_result)
        
        # Sonuçları kaydet
        safe_name = get_safe_filename(pdf_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result_file = save_score_result(
            pdf_file=pdf_file,
            segmentation_file=fixed_file,
            segment=executive_segment,
            score_result=score_result,
            output_prefix="executive",
            timestamp=timestamp
        )
        
        print(f" Sonuçlar JSON olarak kaydedildi: {result_file.name}")
        print(f" Tam yol: {result_file}")
        print()
        print("=" * 70)
        print("İŞLEM TAMAMLANDI!")
        print("=" * 70)
        
    except Exception as e:
        print(f" Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

