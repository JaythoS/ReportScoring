"""
Ortak yardımcı fonksiyonlar - PDF işleme, segmentation, vb.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Yeni core modüllerini kullan
from core.extraction import extract_text_from_pdf, extract_text_from_docx
from core.segmentation import segment_text_chunked, fix_segmentation

# Backward compatibility için eski import'ları da destekle
try:
    from llm.tools.pdf_extractor import extract_text
except ImportError:
    # Eğer eski yapı yoksa, yeni yapıdan extract_text oluştur
    def extract_text(file_path):
        """Backward compatibility için extract_text fonksiyonu"""
        from pathlib import Path
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            return extract_text_from_pdf(path)
        elif path.suffix.lower() == '.docx':
            return extract_text_from_docx(path)
        else:
            return path.read_text(encoding='utf-8')


def get_safe_filename(path: Path) -> str:
    """Dosya adından güvenli bir identifier oluştur"""
    name = path.stem
    safe_name = name.replace(" ", "_").replace(".", "_")
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in safe_name)
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")
    safe_name = safe_name.strip("_")
    return safe_name


def find_pdf_file(pdf_arg: Optional[str], default: str = "ömer_bilbil.pdf") -> Path:
    """
    PDF dosyasını bul ve döndür.
    
    Args:
        pdf_arg: PDF dosya adı veya tam yol
        default: Varsayılan PDF dosya adı
        
    Returns:
        PDF dosya yolu
    """
    if pdf_arg:
        pdf_path = Path(pdf_arg)
        if pdf_path.is_absolute():
            return pdf_path
        else:
            # Önce data/sample_reports'ta ara
            pdf_file = project_root / "data" / "sample_reports" / pdf_arg
            if not pdf_file.exists():
                # Sonra relative path olarak dene
                pdf_file = project_root / pdf_arg
            return pdf_file
    else:
        # Varsayılan dosya
        return project_root / "data" / "sample_reports" / default


def extract_and_segment_pdf(pdf_file: Path) -> tuple[Dict, Path, str]:
    """
    PDF'den metni çıkar, segmentasyon yap ve fix uygula.
    
    Args:
        pdf_file: PDF dosya yolu
        
    Returns:
        (fixed_segmentation_data, fixed_file_path, original_text) tuple
    """
    # 1. Metni çıkar
    print(" Metin çıkarılıyor...")
    text = extract_text(str(pdf_file))
    print(f" Metin çıkarıldı: {len(text):,} karakter")
    print()
    
    # 2. Segmentasyon yap
    print(" Segmentation yapılıyor...")
    print()
    result_json = segment_text_chunked(text)
    
    # Segmentasyon JSON'unu parse et
    seg_data = json.loads(result_json)
    
    # Output klasörü
    output_dir = project_root / "outputs" / "segmentations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Dosya adı
    safe_name = get_safe_filename(pdf_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Segmentasyon dosyasını kaydet
    seg_file = output_dir / f"{safe_name}_Rubric_v3_{timestamp}.json"
    seg_file.write_text(result_json, encoding='utf-8')
    print(f" Segmentation tamamlandı!")
    print(f" Dosya kaydedildi: {seg_file.name}")
    print()
    
    # Özet bilgi
    sections = seg_data.get('segmentation', {}).get('sections', [])
    print(f" Toplam bölüm sayısı: {len(sections)}")
    print()
    
    # 3. Fix segmentation uygula
    print(" Fix segmentation uygulanıyor...")
    print()
    fixed_data = fix_segmentation(seg_file, text)
    
    # Fixed dosyayı kaydet
    fixed_file = seg_file.with_suffix('.fixed.json')
    fixed_file.write_text(
        json.dumps(fixed_data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f" Düzeltilmiş dosya kaydedildi: {fixed_file.name}")
    print()
    
    return fixed_data, fixed_file, text


def save_score_result(
    pdf_file: Path,
    segmentation_file: Path,
    segment: Dict,
    score_result: Dict,
    output_prefix: str,
    timestamp: str
) -> Path:
    """
    Skorlama sonuçlarını JSON olarak kaydet.
    
    Args:
        pdf_file: PDF dosya yolu
        segmentation_file: Segmentation dosya yolu
        segment: Segment dict'i
        score_result: Skorlama sonucu dict'i
        output_prefix: Output dosya öneki (örn: "cover", "executive")
        timestamp: Timestamp string
        
    Returns:
        Kaydedilen dosya yolu
    """
    safe_name = get_safe_filename(pdf_file)
    
    output_result = {
        "pdf_file": pdf_file.name,
        "segmentation_file": segmentation_file.name,
        "segment": {
            "section_id": segment.get("section_id", ""),
            "section_name": segment.get("section_name", ""),
            "content": segment.get("content", ""),
            "level": segment.get("level", 1),
            "parent_id": segment.get("parent_id")
        },
        "score": {
            "total_score": score_result.get("score", 0.0),
            "criteria": score_result.get("criteria", {}),
            "feedback": score_result.get("feedback", "")
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Output klasörü - her score tipi için ayrı klasör
    # outputs/cover_scores/ veya outputs/executive_scores/
    result_output_dir = project_root / "outputs" / f"{output_prefix}_scores"
    result_output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON dosyasını kaydet
    result_file = result_output_dir / f"{safe_name}_{output_prefix}_score_{timestamp}.json"
    result_file.write_text(
        json.dumps(output_result, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    return result_file

