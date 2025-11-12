#!/usr/bin/env python3
"""
Gerçek notlarla test scripti.
ie_drive klasöründeki Excel dosyasından gerçek notları okur ve
bizim LLM çıktılarımızla karşılaştırır.
"""
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.scoring.common import find_pdf_file, extract_and_segment_pdf
from core.scoring import (
    find_executive_summary_segment,
    score_executive_summary
)


def load_real_scores(excel_path: Path) -> pd.DataFrame:
    """
    Excel dosyasından gerçek notları yükle.
    
    Returns:
        DataFrame with columns: Student ID, Current Avg, Letter Grade, ve tüm bölüm notları
    """
    # Header satırı 3 (0-indexed)
    df = pd.read_excel(excel_path, header=3)
    
    # Sütun isimlerini temizle
    df.columns = df.columns.str.strip()
    
    return df


def find_student_pdf(student_id: str, ie_drive_dir: Path) -> Optional[Path]:
    """
    Öğrenci ID'sine göre PDF dosyasını bul.
    
    Args:
        student_id: Öğrenci ID (örn: "akarir")
        ie_drive_dir: ie_drive klasör yolu
        
    Returns:
        PDF dosya yolu veya None
    """
    # Öğrenci ID'si ile başlayan dosyaları ara
    pattern = f"*{student_id}*"
    matches = list(ie_drive_dir.glob(pattern))
    
    # PDF veya DOCX dosyasını bul
    for match in matches:
        if match.suffix.lower() in ['.pdf', '.docx']:
            return match
    
    return None


def test_executive_summary_scoring(
    student_id: str,
    real_score: float,
    max_score: float,
    pdf_file: Path,
    api_key: str = None
) -> Dict:
    """
    Executive Summary notlandırmasını test et.
    
    Args:
        student_id: Öğrenci ID
        real_score: Gerçek not (örn: 6.0)
        max_score: Maksimum not (örn: 6.0)
        pdf_file: PDF dosya yolu
        api_key: Gemini API key
        
    Returns:
        Test sonucu dict'i
    """
    try:
        # PDF'yi işle ve segmentasyon yap
        fixed_data, fixed_file, text = extract_and_segment_pdf(pdf_file)
        
        # Executive Summary segmentini bul
        executive_segment = find_executive_summary_segment(fixed_data)
        
        if not executive_segment:
            return {
                "student_id": student_id,
                "status": "error",
                "error": "Executive Summary segmenti bulunamadı",
                "real_score": real_score,
                "max_score": max_score
            }
        
        # Executive Summary'yi skorla
        score_result = score_executive_summary(executive_segment, api_key)
        
        # LLM'den gelen puan (0-10 arası)
        llm_score_0_10 = score_result.get("score", 0.0)
        
        # 0-10'dan 0-max_score'a çevir
        llm_score_scaled = (llm_score_0_10 / 10.0) * max_score
        
        # Hata hesapla
        error = abs(llm_score_scaled - real_score)
        error_percentage = (error / max_score) * 100 if max_score > 0 else 0
        
        return {
            "student_id": student_id,
            "status": "success",
            "real_score": real_score,
            "max_score": max_score,
            "llm_score_0_10": llm_score_0_10,
            "llm_score_scaled": llm_score_scaled,
            "error": error,
            "error_percentage": error_percentage,
            "criteria": score_result.get("criteria", {}),
            "feedback": score_result.get("feedback", "")[:200]  # İlk 200 karakter
        }
        
    except Exception as e:
        return {
            "student_id": student_id,
            "status": "error",
            "error": str(e),
            "real_score": real_score,
            "max_score": max_score
        }


def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description="Gerçek notlarla Executive Summary notlandırmasını test et"
    )
    parser.add_argument(
        "--student-id",
        type=str,
        default=None,
        help="Belirli bir öğrenci ID'si (test için)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Test edilecek öğrenci sayısı (varsayılan: 5)"
    )
    args = parser.parse_args()
    
    # API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable ayarlanmamış!")
        sys.exit(1)
    
    # Excel dosyasını yükle
    excel_path = project_root / "data" / "ie_drive " / "Book1.xlsx"
    if not excel_path.exists():
        print(f"❌ Excel dosyası bulunamadı: {excel_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("GERÇEK NOTLARLA TEST")
    print("=" * 80)
    print()
    
    df = load_real_scores(excel_path)
    print(f"✅ Excel dosyası yüklendi: {len(df)} öğrenci")
    print(f"   Sütunlar: {list(df.columns[:5])}...")
    print()
    
    # ie_drive klasörü
    ie_drive_dir = project_root / "data" / "ie_drive "
    
    # Test edilecek öğrencileri seç
    if args.student_id:
        students = df[df.iloc[:, 0] == args.student_id]
    else:
        students = df.head(args.limit)
    
    print(f"🧪 {len(students)} öğrenci test edilecek")
    print()
    
    results = []
    
    for idx, row in students.iterrows():
        student_id = str(row.iloc[0])
        real_score = float(row.iloc[3]) if pd.notna(row.iloc[3]) else None  # Executive Summary
        max_score = 6.0  # Executive Summary maksimum puan
        
        if pd.isna(real_score):
            print(f"⚠️  {student_id}: Not bulunamadı, atlanıyor")
            continue
        
        print(f"📄 {student_id}: Gerçek not = {real_score}/{max_score}")
        
        # PDF dosyasını bul
        pdf_file = find_student_pdf(student_id, ie_drive_dir)
        if not pdf_file:
            print(f"   ❌ PDF dosyası bulunamadı")
            results.append({
                "student_id": student_id,
                "status": "error",
                "error": "PDF dosyası bulunamadı",
                "real_score": real_score
            })
            continue
        
        print(f"   📁 PDF: {pdf_file.name}")
        
        # Test et
        result = test_executive_summary_scoring(
            student_id=student_id,
            real_score=real_score,
            max_score=max_score,
            pdf_file=pdf_file,
            api_key=api_key
        )
        
        results.append(result)
        
        if result["status"] == "success":
            print(f"   ✅ LLM Not: {result['llm_score_scaled']:.2f}/{max_score}")
            print(f"   📊 Hata: {result['error']:.2f} ({result['error_percentage']:.1f}%)")
        else:
            print(f"   ❌ Hata: {result.get('error', 'Bilinmeyen hata')}")
        
        print()
    
    # Sonuçları özetle
    print("=" * 80)
    print("SONUÇ ÖZETİ")
    print("=" * 80)
    
    successful = [r for r in results if r["status"] == "success"]
    if successful:
        avg_error = sum(r["error"] for r in successful) / len(successful)
        avg_error_pct = sum(r["error_percentage"] for r in successful) / len(successful)
        
        print(f"✅ Başarılı test: {len(successful)}/{len(results)}")
        print(f"📊 Ortalama hata: {avg_error:.2f} puan ({avg_error_pct:.1f}%)")
        print()
        
        # Detaylı sonuçlar
        print("Detaylı sonuçlar:")
        for r in successful:
            print(f"  {r['student_id']}: Gerçek={r['real_score']:.1f}, "
                  f"LLM={r['llm_score_scaled']:.2f}, "
                  f"Hata={r['error']:.2f} ({r['error_percentage']:.1f}%)")
    
    # Sonuçları JSON olarak kaydet
    output_file = project_root / "outputs" / "test_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_type": "executive_summary",
            "total_tests": len(results),
            "successful": len(successful),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Sonuçlar kaydedildi: {output_file}")


if __name__ == "__main__":
    main()

