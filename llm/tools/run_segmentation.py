#!/usr/bin/env python3
"""
Genel staj raporu segmentation scripti - Rubric'e göre bölümleme
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Proje root'unu path'e ekle (tools/ klasöründen 2 seviye yukarı: tools -> llm -> root)
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from llm.tools.pdf_extractor import extract_text
from llm.tools.gemini_segment_chunked import segment_text_chunked
from llm.tools.fix_segmentation import fix_segmentation
from llm.tools.validate_segmentation import validate_segmentation


def get_safe_filename(path: Path) -> str:
    """Dosya adından güvenli bir identifier oluştur"""
    # Dosya adını al (uzantı olmadan)
    name = path.stem
    # Özel karakterleri temizle ve boşlukları alt çizgi ile değiştir
    safe_name = name.replace(" ", "_").replace(".", "_")
    # Türkçe karakterleri ve özel karakterleri temizle
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in safe_name)
    # Çoklu alt çizgileri tek alt çizgiye çevir
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")
    # Başındaki/sonundaki alt çizgileri temizle
    safe_name = safe_name.strip("_")
    return safe_name


def list_available_reports(reports_dir: Path) -> list:
    """Sample reports klasöründeki PDF dosyalarını listele"""
    pdf_files = sorted(reports_dir.glob("*.pdf"))
    return pdf_files


def main():
    parser = argparse.ArgumentParser(
        description="Staj raporu segmentation scripti - Rubric'e göre bölümleme",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanım:
  # Dosya path'i ile
  python3 llm/tools/run_segmentation.py --pdf "data/sample_reports/Doğuş Teknoloji Intern Report LAST.docx .pdf"
  
  # Mutlak path ile
  python3 llm/tools/run_segmentation.py --pdf /path/to/report.pdf
  
  # Sample reports klasöründen seçim (interactive)
  python3 llm/tools/run_segmentation.py
        """
    )
    
    parser.add_argument(
        "--pdf",
        type=str,
        help="PDF dosyasının path'i (relative veya absolute)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output klasörü (varsayılan: outputs/segmentations)"
    )
    
    parser.add_argument(
        "--rubric-version",
        type=str,
        default="v3",
        help="Rubric versiyonu (varsayılan: v3)"
    )
    
    args = parser.parse_args()
    
    # PDF dosyasını bul
    pdf_file = None
    
    if args.pdf:
        # Komut satırından verilen path
        pdf_path = Path(args.pdf)
        if pdf_path.is_absolute():
            pdf_file = pdf_path
        else:
            # Relative path - önce current directory'de, sonra project root'ta ara
            if pdf_path.exists():
                pdf_file = pdf_path.resolve()
            else:
                pdf_file = (project_root / pdf_path).resolve()
    else:
        # Interactive mod: sample_reports klasöründen seç
        reports_dir = project_root / "data" / "sample_reports"
        if not reports_dir.exists():
            print(f"❌ Sample reports klasörü bulunamadı: {reports_dir}")
            sys.exit(1)
        
        pdf_files = list_available_reports(reports_dir)
        
        if not pdf_files:
            print(f"❌ {reports_dir} klasöründe PDF dosyası bulunamadı")
            sys.exit(1)
        
        print("=" * 70)
        print("MEVCUT RAPORLAR")
        print("=" * 70)
        print()
        for i, pdf in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf.name}")
        print()
        
        try:
            choice = input("Seçim yapın (1-{}): ".format(len(pdf_files)))
            idx = int(choice) - 1
            if 0 <= idx < len(pdf_files):
                pdf_file = pdf_files[idx]
            else:
                print("❌ Geçersiz seçim")
                sys.exit(1)
        except (ValueError, KeyboardInterrupt):
            print("\n❌ İşlem iptal edildi")
            sys.exit(1)
    
    # Dosya kontrolü
    if not pdf_file or not pdf_file.exists():
        print(f"❌ Dosya bulunamadı: {pdf_file}")
        sys.exit(1)
    
    # Output dosya adını oluştur
    safe_name = get_safe_filename(pdf_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 70)
    print(f"STAJ RAPORU SEGMENTATION (RUBRIC {args.rubric_version.upper()})")
    print("=" * 70)
    print()
    print(f"📄 Rapor: {pdf_file.name}")
    print()
    
    # Metni çıkar
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
    
    # Segmentasyon yap
    print("🔍 Segmentation yapılıyor (chunked)...")
    print()
    try:
        result_json = segment_text_chunked(text)
        
        # Sonuçları kaydet
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = project_root / "outputs" / "segmentations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{safe_name}_Rubric_{args.rubric_version}_{timestamp}.json"
        
        output_file.write_text(result_json, encoding='utf-8')
        print()
        print(f"✅ Segmentation tamamlandı!")
        print(f"📁 Dosya kaydedildi: {output_file.name}")
        print()
        
        # Özet bilgi
        import json
        data = json.loads(result_json)
        sections = data.get('segmentation', {}).get('sections', [])
        print(f"📊 Toplam bölüm sayısı: {len(sections)}")
        print()
        
        # Fix segmentation uygula
        print("🔧 Fix segmentation uygulanıyor...")
        print()
        fixed_data = fix_segmentation(output_file, text)
        
        # Fixed dosyayı kaydet
        fixed_file = output_file.with_suffix('.fixed.json')
        fixed_file.write_text(
            json.dumps(fixed_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print()
        print(f"✅ Düzeltilmiş dosya kaydedildi: {fixed_file.name}")
        print()
        
        # Validation
        print("🔍 Validation yapılıyor...")
        print()
        validation_result = validate_segmentation(fixed_file)
        
        from llm.tools.validate_segmentation import print_validation_report
        print_validation_report(validation_result)
        
    except Exception as e:
        print(f"❌ Segmentation hatası: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
