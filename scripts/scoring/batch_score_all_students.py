#!/usr/bin/env python3
"""
Tüm öğrenciler için batch scoring scripti.
ie_drive klasöründeki tüm PDF'leri notlandırır ve Excel'deki gerçek notlarla karşılaştırır.
"""
import sys
import json
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.scoring.common import extract_and_segment_pdf
from core.scoring import (
    find_cover_segment,
    find_executive_summary_segment,
    score_cover_segment,
    score_executive_summary
)
from core.anonymization import Anonymizer


def load_real_scores(excel_path: Path) -> pd.DataFrame:
    """
    Excel dosyasından gerçek notları yükle.
    
    Returns:
        DataFrame with student scores
    """
    df = pd.read_excel(excel_path, header=3)
    df.columns = df.columns.str.strip()
    return df


def find_student_file(student_id: str, ie_drive_dir: Path) -> Optional[Path]:
    """
    Öğrenci ID'sine göre PDF/DOCX dosyasını bul.
    """
    # Öğrenci ID'si ile başlayan dosyaları ara
    pattern = f"*{student_id}*"
    matches = list(ie_drive_dir.glob(pattern))
    
    # PDF veya DOCX dosyasını bul
    for match in matches:
        if match.suffix.lower() in ['.pdf', '.docx']:
            return match
    
    return None


def score_student_report(
    student_id: str,
    pdf_file: Path,
    api_key: str,
    score_cover: bool = False,
    score_executive: bool = True
) -> Dict:
    """
    Bir öğrencinin raporunu notlandır.
    
    Returns:
        {
            "student_id": str,
            "status": "success" | "error",
            "cover_score": float | None,
            "executive_score": float | None,
            "error": str | None
        }
    """
    result = {
        "student_id": student_id,
        "status": "error",
        "cover_score": None,
        "executive_score": None,
        "error": None
    }
    
    try:
        # PDF'yi işle ve segmentasyon yap
        fixed_data, fixed_file, text = extract_and_segment_pdf(pdf_file)
        
        scores = {}
        
        # Cover scoring
        if score_cover:
            cover_segment = find_cover_segment(fixed_data)
            if cover_segment:
                cover_result = score_cover_segment(cover_segment, api_key)
                scores["cover"] = {
                    "score_0_10": cover_result.get("score", 0.0),
                    "score_scaled_0_10": cover_result.get("score", 0.0),  # Cover zaten 0-10
                    "criteria": cover_result.get("criteria", {})
                }
                result["cover_score"] = cover_result.get("score", 0.0)
        
        # Executive Summary scoring
        if score_executive:
            executive_segment = find_executive_summary_segment(fixed_data)
            if executive_segment:
                # Executive Summary'yi anonimleştir
                original_content = executive_segment.get("content", "")
                anonymizer = Anonymizer()
                anonymized_content, _ = anonymizer.anonymize_text(original_content, student_id)
                
                # Anonimleştirilmiş içeriği kullan
                executive_segment_anon = executive_segment.copy()
                executive_segment_anon["content"] = anonymized_content
                
                executive_result = score_executive_summary(executive_segment_anon, api_key)
                # Executive Summary maksimum 6 puan (0-6 arası)
                # Kriter ortalamasını kullan (LLM'in döndürdüğü score değil)
                criteria = executive_result.get("criteria", {})
                if criteria:
                    # Kriter ortalamasını hesapla
                    criteria_avg = sum(criteria.values()) / len(criteria)
                else:
                    # Fallback: LLM'in döndürdüğü score değerini kullan
                    criteria_avg = executive_result.get("score", 0.0)
                
                llm_score_scaled_0_6 = (criteria_avg / 10.0) * 6.0
                
                scores["executive"] = {
                    "score_0_10": criteria_avg,  # Kriter ortalaması
                    "score_scaled_0_6": llm_score_scaled_0_6,
                    "criteria": criteria
                }
                result["executive_score"] = llm_score_scaled_0_6
            else:
                result["error"] = "Executive Summary segmenti bulunamadı"
                return result
        
        result["status"] = "success"
        result["scores"] = scores
        result["segmentation_file"] = fixed_file.name
        
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result


def compare_with_real_scores(
    llm_results: List[Dict],
    real_scores_df: pd.DataFrame
) -> pd.DataFrame:
    """
    LLM sonuçlarını gerçek notlarla karşılaştır.
    
    Returns:
        DataFrame with comparison results
    """
    comparison_data = []
    
    for result in llm_results:
        if result["status"] != "success":
            continue
        
        student_id = result["student_id"]
        
        # Gerçek notu bul
        student_row = real_scores_df[real_scores_df.iloc[:, 0] == student_id]
        if student_row.empty:
            continue
        
        real_executive = float(student_row.iloc[0, 3]) if pd.notna(student_row.iloc[0, 3]) else None
        
        if real_executive is None:
            continue
        
        llm_executive = result.get("executive_score")
        if llm_executive is None:
            continue
        
        # Hata hesapla
        error = abs(llm_executive - real_executive)
        error_percentage = (error / 6.0) * 100 if 6.0 > 0 else 0
        
        comparison_data.append({
            "student_id": student_id,
            "real_executive_score": real_executive,
            "llm_executive_score": llm_executive,
            "error": error,
            "error_percentage": error_percentage,
            "real_cover_score": float(student_row.iloc[0, 11]) if pd.notna(student_row.iloc[0, 11]) else None,
            "llm_cover_score": result.get("cover_score")
        })
    
    return pd.DataFrame(comparison_data)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Tüm öğrenciler için batch scoring ve gerçek notlarla karşılaştırma"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Test edilecek öğrenci sayısı (varsayılan: tümü)"
    )
    parser.add_argument(
        "--score-cover",
        action="store_true",
        help="Cover'ı da notlandır"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Zaten notlandırılmış öğrencileri atla"
    )
    args = parser.parse_args()
    
    # API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(" GEMINI_API_KEY environment variable ayarlanmamış!")
        sys.exit(1)
    
    print("=" * 80)
    print("BATCH SCORING - TÜM ÖĞRENCİLER")
    print("=" * 80)
    print()
    
    # Excel dosyasını yükle
    excel_path = project_root / "data" / "ie_drive " / "Book1.xlsx"
    if not excel_path.exists():
        print(f" Excel dosyası bulunamadı: {excel_path}")
        sys.exit(1)
    
    real_scores_df = load_real_scores(excel_path)
    print(f" Excel dosyası yüklendi: {len(real_scores_df)} öğrenci")
    print()
    
    # ie_drive klasörü
    ie_drive_dir = project_root / "data" / "ie_drive "
    
    # Öğrencileri seç
    students = real_scores_df
    if args.limit:
        students = students.head(args.limit)
    
    print(f" {len(students)} öğrenci notlandırılacak")
    print()
    
    # Mevcut sonuçları yükle (eğer varsa)
    results_file = project_root / "outputs" / "batch_scoring_results.json"
    existing_results = []
    if args.skip_existing and results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_results = existing_data.get("results", [])
            existing_ids = {r["student_id"] for r in existing_results if r.get("status") == "success"}
            print(f" {len(existing_ids)} öğrenci zaten notlandırılmış, atlanacak")
            print()
    
    results = existing_results.copy()
    existing_ids = {r["student_id"] for r in existing_results}
    
    # Her öğrenciyi notlandır
    for idx, row in tqdm(students.iterrows(), total=len(students), desc="Notlandırılıyor"):
        student_id = str(row.iloc[0])
        
        # Zaten varsa atla
        if args.skip_existing and student_id in existing_ids:
            continue
        
        # PDF dosyasını bul
        pdf_file = find_student_file(student_id, ie_drive_dir)
        if not pdf_file:
            results.append({
                "student_id": student_id,
                "status": "error",
                "error": "PDF/DOCX dosyası bulunamadı"
            })
            continue
        
        # Notlandır
        result = score_student_report(
            student_id=student_id,
            pdf_file=pdf_file,
            api_key=api_key,
            score_cover=args.score_cover,
            score_executive=True
        )
        
        results.append(result)
        
        # Her 10 öğrencide bir kaydet (ilerleme kaybını önlemek için)
        if len(results) % 10 == 0:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_type": "batch_scoring",
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(results),
                    "results": results
                }, f, ensure_ascii=False, indent=2)
    
    # Sonuçları kaydet
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_type": "batch_scoring",
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 80)
    print("SONUÇLAR KAYDEDİLDİ")
    print("=" * 80)
    print(f" Dosya: {results_file}")
    print()
    
    # Gerçek notlarla karşılaştır
    comparison_df = compare_with_real_scores(results, real_scores_df)
    
    if len(comparison_df) > 0:
        print("=" * 80)
        print("GERÇEK NOTLARLA KARŞILAŞTIRMA")
        print("=" * 80)
        print()
        
        avg_error = comparison_df["error"].mean()
        avg_error_pct = comparison_df["error_percentage"].mean()
        
        print(f" Başarılı karşılaştırma: {len(comparison_df)}/{len(results)}")
        print(f" Ortalama hata: {avg_error:.2f} puan ({avg_error_pct:.1f}%)")
        print()
        
        # İstatistikler
        print("Hata dağılımı:")
        print(comparison_df["error"].describe())
        print()
        
        # En iyi ve en kötü sonuçlar
        comparison_df_sorted = comparison_df.sort_values("error")
        print("En iyi 5 sonuç (en düşük hata):")
        print(comparison_df_sorted.head(5)[["student_id", "real_executive_score", "llm_executive_score", "error"]].to_string(index=False))
        print()
        
        print("En kötü 5 sonuç (en yüksek hata):")
        print(comparison_df_sorted.tail(5)[["student_id", "real_executive_score", "llm_executive_score", "error"]].to_string(index=False))
        
        # CSV olarak kaydet
        csv_file = project_root / "outputs" / "comparison_results.csv"
        comparison_df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"\n Karşılaştırma sonuçları CSV olarak kaydedildi: {csv_file}")
    
    print()
    print("=" * 80)
    print("İŞLEM TAMAMLANDI!")
    print("=" * 80)


if __name__ == "__main__":
    main()

