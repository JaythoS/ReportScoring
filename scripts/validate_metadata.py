#!/usr/bin/env python3
"""
Metadata Validation Scripti

Metadata JSON dosyalarını şemaya göre doğrular.
"""
import sys
import json
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def validate_metadata(metadata_path: Path, schema_path: Path) -> tuple[bool, list]:
    """
    Metadata dosyasını şemaya göre doğrula
    
    Args:
        metadata_path: Metadata JSON dosyası yolu
        schema_path: JSON Schema dosyası yolu
    
    Returns:
        (is_valid, errors) tuple
    """
    try:
        import jsonschema
    except ImportError:
        print("⚠️  jsonschema paketi yüklü değil. Basit validation yapılıyor...")
        return validate_metadata_simple(metadata_path, schema_path)
    
    # Şemayı yükle
    try:
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ Şema yüklenemedi: {e}")
        return False, [f"Schema load error: {e}"]
    
    # Metadata'yı yükle
    try:
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ Metadata yüklenemedi: {e}")
        return False, [f"Metadata load error: {e}"]
    
    # Validate et
    errors = []
    try:
        jsonschema.validate(instance=metadata, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        errors.append(f"Validation error: {e.message}")
        if e.path:
            errors.append(f"  Path: {'.'.join(str(p) for p in e.path)}")
        return False, errors
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, errors


def validate_metadata_simple(metadata_path: Path, schema_path: Path) -> tuple[bool, list]:
    """Basit validation (jsonschema olmadan)"""
    errors = []
    
    # Metadata'yı yükle
    try:
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, [f"JSON parse error: {e}"]
    
    # Zorunlu alanları kontrol et
    required_fields = ["report_id", "filename", "timestamp", "file_paths"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # Report ID formatını kontrol et
    if "report_id" in metadata:
        report_id = metadata["report_id"]
        if not report_id.startswith("report_") or len(report_id) != 11:
            errors.append(f"Invalid report_id format: {report_id} (expected: report_XXX)")
    
    # File paths kontrolü
    if "file_paths" in metadata:
        file_paths = metadata["file_paths"]
        if "raw_file" not in file_paths:
            errors.append("Missing required field: file_paths.raw_file")
    
    return len(errors) == 0, errors


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Metadata JSON dosyasını şemaya göre doğrula",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "metadata_file",
        type=str,
        help="Metadata JSON dosyası yolu"
    )
    
    parser.add_argument(
        "--schema",
        type=str,
        default=None,
        help="JSON Schema dosyası yolu (varsayılan: schemas/metadata.schema.json)"
    )
    
    args = parser.parse_args()
    
    # Dosya yollarını belirle
    metadata_path = Path(args.metadata_file)
    if not metadata_path.exists():
        print(f"❌ Metadata dosyası bulunamadı: {metadata_path}")
        sys.exit(1)
    
    if args.schema:
        schema_path = Path(args.schema)
    else:
        schema_path = project_root / "schemas" / "metadata.schema.json"
    
    if not schema_path.exists():
        print(f"⚠️  Şema dosyası bulunamadı: {schema_path}")
        print("   Basit validation yapılıyor...")
        schema_path = None
    
    print("=" * 70)
    print("METADATA VALIDATION")
    print("=" * 70)
    print(f"📄 Metadata: {metadata_path}")
    if schema_path:
        print(f"📋 Schema: {schema_path}")
    print()
    
    # Validate et
    if schema_path:
        is_valid, errors = validate_metadata(metadata_path, schema_path)
    else:
        is_valid, errors = validate_metadata_simple(metadata_path, Path("/dev/null"))
    
    # Sonuçları göster
    if is_valid:
        print("✅ Metadata geçerli!")
        print()
        
        # Metadata bilgilerini göster
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        print("📊 Metadata Bilgileri:")
        print(f"   Report ID: {metadata.get('report_id', 'N/A')}")
        print(f"   Filename: {metadata.get('filename', 'N/A')}")
        print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")
        print(f"   Version: {metadata.get('version', 'N/A')}")
        if 'scores' in metadata and 'total' in metadata['scores']:
            print(f"   Total Score: {metadata['scores']['total']}")
        if 'dataset_split' in metadata:
            print(f"   Dataset Split: {metadata['dataset_split']}")
    else:
        print("❌ Metadata geçersiz!")
        print()
        print("Hatalar:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

