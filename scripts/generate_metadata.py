#!/usr/bin/env python3
"""
Metadata Generator Scripti

Staj raporu için metadata.json dosyası oluşturur.
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def calculate_file_hash(file_path: Path) -> str:
    """Dosyanın SHA-256 hash'ini hesapla"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_text_hash(text: str) -> str:
    """Metnin SHA-256 hash'ini hesapla"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def extract_report_id(filename: str) -> str:
    """Dosya adından report_id çıkar (report_XXX formatında)"""
    # Dosya adından stem'i al (uzantıyı çıkar)
    stem = Path(filename).stem
    
    # Eğer zaten report_XXX formatındaysa
    if stem.startswith("report_") and len(stem) >= 11:
        # report_XXX formatını kontrol et
        if stem[7:10].isdigit():
            return stem[:11]  # report_XXX
        # report_XXX.xxx formatını kontrol et
        if len(stem) > 11 and stem[7:10].isdigit():
            return stem[:11]
    
    # Fallback: Dosya adından ID oluştur
    # İlk 3 karakteri al ve report_XXX formatına çevir
    clean_stem = stem.replace(".", "").replace(" ", "_")
    if len(clean_stem) >= 7 and clean_stem.startswith("report_"):
        # report_XXX formatını bul
        match = ""
        for i in range(7, min(len(clean_stem), 11)):
            if clean_stem[i].isdigit():
                match += clean_stem[i]
            else:
                break
        if len(match) == 3:
            return f"report_{match}"
    
    # Son çare: report_000
    return "report_000"


def generate_metadata(
    report_id: str,
    filename: str,
    raw_file_path: Path,
    text_file_path: Optional[Path] = None,
    segmentation_file_path: Optional[Path] = None,
    dataset_split: Optional[str] = None,
    scores: Optional[Dict[str, Any]] = None,
    criteria: Optional[Dict[str, Any]] = None,
    processing_info: Optional[Dict[str, Any]] = None,
    version: str = "v1"
) -> Dict[str, Any]:
    """
    Metadata dosyası oluştur
    
    Args:
        report_id: Rapor ID'si (örn: report_001)
        filename: Dosya adı
        raw_file_path: Ham dosya yolu
        text_file_path: Metin dosyası yolu (opsiyonel)
        segmentation_file_path: Bölümleme dosyası yolu (opsiyonel)
        dataset_split: Veri seti ayrımı (train/test)
        scores: Puanlar (opsiyonel)
        criteria: Kriterler (opsiyonel)
        processing_info: İşleme bilgileri (opsiyonel)
        version: Metadata versiyonu
    
    Returns:
        Metadata dictionary
    """
    # Dosya yolları (absolute path'leri relative'e çevir)
    def to_relative_path(path: Path) -> str:
        try:
            if path.is_absolute():
                return str(path.relative_to(project_root))
            else:
                return str(path)
        except ValueError:
            # Eğer relative path'e çevrilemiyorsa, absolute path'i kullan
            return str(path)
    
    file_paths = {
        "raw_file": to_relative_path(raw_file_path.resolve())
    }
    
    if text_file_path and text_file_path.exists():
        file_paths["text_file"] = to_relative_path(text_file_path.resolve())
    
    if segmentation_file_path and segmentation_file_path.exists():
        file_paths["segmentation_file"] = to_relative_path(segmentation_file_path.resolve())
    
    metadata_file_path = project_root / "data" / "processed" / "metadata" / f"{report_id}_metadata.json"
    file_paths["metadata_file"] = to_relative_path(metadata_file_path)
    
    # Hash hesapla
    file_hash = None
    text_hash = None
    
    if raw_file_path.exists():
        file_hash = calculate_file_hash(raw_file_path)
    
    if text_file_path and text_file_path.exists():
        text_content = text_file_path.read_text(encoding='utf-8')
        text_hash = calculate_text_hash(text_content)
    
    # Metadata oluştur
    metadata = {
        "report_id": report_id,
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "version": version,
        "file_paths": file_paths
    }
    
    # Opsiyonel alanlar
    if scores:
        metadata["scores"] = scores
    
    if criteria:
        metadata["criteria"] = criteria
    
    if processing_info:
        metadata["processing_info"] = processing_info
    
    if file_hash:
        metadata["file_hash"] = file_hash
    
    if text_hash:
        metadata["text_hash"] = text_hash
    
    if dataset_split:
        metadata["dataset_split"] = dataset_split
    
    return metadata


def save_metadata(metadata: Dict[str, Any], output_path: Path):
    """Metadata'yı JSON dosyasına kaydet"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Staj raporu için metadata.json dosyası oluştur",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--report-id",
        type=str,
        help="Rapor ID'si (örn: report_001). Belirtilmezse dosya adından çıkarılır."
    )
    
    parser.add_argument(
        "--raw-file",
        type=str,
        required=True,
        help="Ham PDF/DOCX dosyası yolu"
    )
    
    parser.add_argument(
        "--text-file",
        type=str,
        help="Çıkarılmış metin dosyası yolu (opsiyonel)"
    )
    
    parser.add_argument(
        "--segmentation-file",
        type=str,
        help="Bölümleme çıktısı dosyası yolu (opsiyonel)"
    )
    
    parser.add_argument(
        "--dataset-split",
        type=str,
        choices=["train", "test", "validation"],
        help="Veri seti ayrımı (train/test)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Çıktı dosyası yolu (varsayılan: data/processed/metadata/{report_id}_metadata.json)"
    )
    
    args = parser.parse_args()
    
    # Dosya yollarını kontrol et
    raw_file_path = Path(args.raw_file)
    if not raw_file_path.is_absolute():
        raw_file_path = (project_root / raw_file_path).resolve()
    
    if not raw_file_path.exists():
        print(f" Ham dosya bulunamadı: {raw_file_path}")
        sys.exit(1)
    
    # Report ID'yi belirle
    if args.report_id:
        report_id = args.report_id
    else:
        report_id = extract_report_id(raw_file_path.name)
    
    filename = raw_file_path.name
    
    # Diğer dosya yolları
    if args.text_file:
        text_file_path = Path(args.text_file)
        if not text_file_path.is_absolute():
            text_file_path = (project_root / text_file_path).resolve()
    else:
        text_file_path = None
    
    if args.segmentation_file:
        segmentation_file_path = Path(args.segmentation_file)
        if not segmentation_file_path.is_absolute():
            segmentation_file_path = (project_root / segmentation_file_path).resolve()
    else:
        segmentation_file_path = None
    
    # Çıktı dosyası
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "data" / "processed" / "metadata" / f"{report_id}_metadata.json"
    
    print("=" * 70)
    print("METADATA OLUŞTURULUYOR")
    print("=" * 70)
    print(f" Rapor ID: {report_id}")
    print(f" Dosya: {filename}")
    print()
    
    # Metadata oluştur
    metadata = generate_metadata(
        report_id=report_id,
        filename=filename,
        raw_file_path=raw_file_path,
        text_file_path=text_file_path,
        segmentation_file_path=segmentation_file_path,
        dataset_split=args.dataset_split
    )
    
    # Kaydet
    save_metadata(metadata, output_path)
    
    print(f" Metadata oluşturuldu: {output_path}")
    print()
    print(" Özet:")
    print(f"   Report ID: {metadata['report_id']}")
    print(f"   Timestamp: {metadata['timestamp']}")
    print(f"   Version: {metadata['version']}")
    if 'file_hash' in metadata:
        print(f"   File Hash: {metadata['file_hash'][:16]}...")
    if 'dataset_split' in metadata:
        print(f"   Dataset Split: {metadata['dataset_split']}")
    print()


if __name__ == "__main__":
    main()

