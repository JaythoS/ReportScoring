#!/usr/bin/env python3
"""
PDF dosyasını segment et, cover ve executive summary kısımlarını skorla ve JSON olarak kaydet
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from llm.tools.pdf_extractor import extract_text
from llm.tools.gemini_segment_chunked import segment_text_chunked
from llm.tools.fix_segmentation import fix_segmentation
from src.analyze.segment_scoring import (
    find_cover_segment, 
    find_executive_summary_segment,
    score_cover_segment,
    score_executive_summary
)


def get_safe_filename(path: Path) -> str:
    """Dosya adından güvenli bir identifier oluştur"""
    name = path.stem
    safe_name = name.replace(" ", "_").replace(".", "_")
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in safe_name)
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")
    safe_name = safe_name.strip("_")
    return safe_name


def main():
    parser = argparse.ArgumentParser(
        description="PDF dosyasını segment et, cover ve executive summary kısımlarını skorla ve JSON olarak kaydet"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="PDF dosya adı (data/sample_reports klasöründen) veya tam yol"
    )
    args = parser.parse_args()
    
    # PDF dosyasını bul
    if args.pdf:
        pdf_path = Path(args.pdf)
        if pdf_path.is_absolute():
            pdf_file = pdf_path
        else:
            # Önce data/sample_reports'ta ara
            pdf_file = project_root / "data" / "sample_reports" / args.pdf
            if not pdf_file.exists():
                # Sonra relative path olarak dene
                pdf_file = project_root / args.pdf
    else:
        # Varsayılan olarak ömer_bilbil.pdf
        pdf_file = project_root / "data" / "sample_reports" / "ömer_bilbil.pdf"
    
    if not pdf_file.exists():
        print(f"❌ PDF dosyası bulunamadı: {pdf_file}")
        sys.exit(1)
    
    # Güvenli dosya adı oluştur
    safe_name = get_safe_filename(pdf_file)
    
    print("=" * 70)
    print("PDF İŞLEME - SEGMENTASYON, COVER VE EXECUTIVE SUMMARY SKORLAMA")
    print("=" * 70)
    print()
    print(f"📄 Rapor: {pdf_file.name}")
    print()
    
    # 1. Metni çıkar
    print("📄 Metin çıkarılıyor...")
    try:
        text = extract_text(str(pdf_file))
        print(f"✅ Metin çıkarıldı: {len(text):,} karakter")
        print()
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 2. Segmentasyon yap
    print("🔍 Segmentation yapılıyor...")
    print()
    try:
        result_json = segment_text_chunked(text)
        
        # Segmentasyon JSON'unu parse et
        seg_data = json.loads(result_json)
        
        # Output klasörü
        output_dir = project_root / "outputs" / "segmentations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Segmentasyon dosyasını kaydet
        seg_file = output_dir / f"{safe_name}_Rubric_v3_{timestamp}.json"
        seg_file.write_text(result_json, encoding='utf-8')
        print(f"✅ Segmentation tamamlandı!")
        print(f"📁 Dosya kaydedildi: {seg_file.name}")
        print()
        
        # Özet bilgi
        sections = seg_data.get('segmentation', {}).get('sections', [])
        print(f"📊 Toplam bölüm sayısı: {len(sections)}")
        print()
        
        # 3. Fix segmentation uygula
        print("🔧 Fix segmentation uygulanıyor...")
        print()
        fixed_data = fix_segmentation(seg_file, text)
        
        # Fixed dosyayı kaydet
        fixed_file = seg_file.with_suffix('.fixed.json')
        fixed_file.write_text(
            json.dumps(fixed_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"✅ Düzeltilmiş dosya kaydedildi: {fixed_file.name}")
        print()
        
        # 4. Cover segmentini bul
        print("🔍 Cover segmenti aranıyor...")
        print()
        cover_segment = find_first_segment(fixed_data)
        
        if not cover_segment:
            print("❌ Cover segmenti bulunamadı!")
            sys.exit(1)
        
        print(f"✅ Cover segmenti bulundu:")
        print(f"   - Section ID: {cover_segment.get('section_id', 'unknown')}")
        print(f"   - Section Name: {cover_segment.get('section_name', 'unknown')}")
        print(f"   - Content uzunluğu: {len(cover_segment.get('content', ''))} karakter")
        print()
        
        # 5. Cover'ı skorla
        print("📊 Cover skorlanıyor...")
        print()
        try:
            score_result = score_segment(cover_segment)
            
            print(f"✅ Skorlama tamamlandı!")
            print(f"   📊 Toplam Puan: {score_result.get('score', 0.0):.2f}/10")
            print(f"   - Başlık Doğruluğu: {score_result.get('criteria', {}).get('title_accuracy', 0.0):.2f}/10")
            print(f"   - Biçim: {score_result.get('criteria', {}).get('format', 0.0):.2f}/10")
            print(f"   - Bilgi Tamlığı: {score_result.get('criteria', {}).get('completeness', 0.0):.2f}/10")
            print(f"   - Tarih/İsim Varlığı: {score_result.get('criteria', {}).get('date_name_presence', 0.0):.2f}/10")
            print()
            
            # 6. Sonuçları JSON olarak kaydet
            output_result = {
                "pdf_file": pdf_file.name,
                "segmentation_file": fixed_file.name,
                "cover_segment": {
                    "section_id": cover_segment.get("section_id", ""),
                    "section_name": cover_segment.get("section_name", ""),
                    "content": cover_segment.get("content", ""),
                    "level": cover_segment.get("level", 1),
                    "parent_id": cover_segment.get("parent_id")
                },
                "score": {
                    "total_score": score_result.get("score", 0.0),
                    "criteria": score_result.get("criteria", {}),
                    "feedback": score_result.get("feedback", "")
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Output klasörü
            result_output_dir = project_root / "outputs"
            result_output_dir.mkdir(parents=True, exist_ok=True)
            
            # JSON dosyasını kaydet
            result_file = result_output_dir / f"{safe_name}_cover_score_{timestamp}.json"
            result_file.write_text(
                json.dumps(output_result, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            print(f"✅ Sonuçlar JSON olarak kaydedildi: {result_file.name}")
            print(f"📁 Tam yol: {result_file}")
            print()
            print("=" * 70)
            print("İŞLEM TAMAMLANDI!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Skorlama hatası: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Segmentation hatası: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

