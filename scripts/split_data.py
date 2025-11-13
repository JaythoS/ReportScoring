#!/usr/bin/env python3
"""
Train/Test Ayrımı Scripti

150 raporu train (120) ve test (30) setlerine ayırır.
"""
import sys
import json
import random
import shutil
from pathlib import Path
from datetime import datetime

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def get_report_files(raw_dir: Path) -> list:
    """Raw klasöründeki tüm rapor dosyalarını listele"""
    pdf_files = list(raw_dir.glob("*.pdf"))
    docx_files = list(raw_dir.glob("*.docx"))
    return sorted(pdf_files + docx_files)


def split_reports(reports: list, train_ratio: float = 0.8, random_seed: int = 42) -> tuple:
    """
    Raporları train ve test setlerine ayırır.
    
    Args:
        reports: Rapor dosyalarının listesi
        train_ratio: Train seti oranı (varsayılan: 0.8 = %80)
        random_seed: Rastgelelik tohumu (reproducibility için)
    
    Returns:
        (train_reports, test_reports) tuple
    """
    # Reproducibility için random seed
    random.seed(random_seed)
    
    # Raporları karıştır
    shuffled_reports = reports.copy()
    random.shuffle(shuffled_reports)
    
    # Train/Test ayrımı
    train_size = int(len(shuffled_reports) * train_ratio)
    train_reports = shuffled_reports[:train_size]
    test_reports = shuffled_reports[train_size:]
    
    return train_reports, test_reports


def copy_reports(reports: list, source_dir: Path, target_dir: Path) -> int:
    """Raporları kaynak klasörden hedef klasöre kopyala"""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for report in reports:
        target_file = target_dir / report.name
        try:
            shutil.copy2(report, target_file)
            copied += 1
        except Exception as e:
            print(f"  Hata: {report.name} kopyalanamadı: {e}")
    
    return copied


def save_split_info(train_reports: list, test_reports: list, output_file: Path):
    """Train/Test ayrım bilgisini JSON dosyasına kaydet"""
    split_info = {
        "train": [r.stem for r in train_reports],
        "test": [r.stem for r in test_reports],
        "train_count": len(train_reports),
        "test_count": len(test_reports),
        "total_count": len(train_reports) + len(test_reports),
        "train_ratio": len(train_reports) / (len(train_reports) + len(test_reports)),
        "split_date": datetime.now().isoformat(),
        "split_method": "random",
        "random_seed": 42
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(split_info, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def main():
    """Ana fonksiyon"""
    # Klasör yolları
    raw_dir = project_root / "data" / "raw"
    train_dir = project_root / "data" / "train"
    test_dir = project_root / "data" / "test"
    split_info_file = project_root / "data" / "split_info.json"
    
    # Raw klasörü kontrolü
    if not raw_dir.exists():
        print(f" Raw klasörü bulunamadı: {raw_dir}")
        sys.exit(1)
    
    # Rapor dosyalarını al
    print(" Rapor dosyaları aranıyor...")
    reports = get_report_files(raw_dir)
    
    if not reports:
        print(f" {raw_dir} klasöründe rapor dosyası bulunamadı")
        print("   Lütfen PDF veya DOCX dosyalarını data/raw/ klasörüne ekleyin")
        sys.exit(1)
    
    print(f" {len(reports)} rapor dosyası bulundu")
    print()
    
    # Train/Test ayrımı
    print(" Train/Test ayrımı yapılıyor...")
    train_reports, test_reports = split_reports(reports, train_ratio=0.8, random_seed=42)
    
    print(f"   Train: {len(train_reports)} rapor (%{len(train_reports)/len(reports)*100:.1f})")
    print(f"   Test: {len(test_reports)} rapor (%{len(test_reports)/len(reports)*100:.1f})")
    print()
    
    # Train setini kopyala
    print(" Train seti kopyalanıyor...")
    train_copied = copy_reports(train_reports, raw_dir, train_dir)
    print(f" {train_copied}/{len(train_reports)} rapor kopyalandı")
    print()
    
    # Test setini kopyala
    print(" Test seti kopyalanıyor...")
    test_copied = copy_reports(test_reports, raw_dir, test_dir)
    print(f" {test_copied}/{len(test_reports)} rapor kopyalandı")
    print()
    
    # Ayrım bilgisini kaydet
    print(" Ayrım bilgisi kaydediliyor...")
    save_split_info(train_reports, test_reports, split_info_file)
    print(f" Ayrım bilgisi kaydedildi: {split_info_file}")
    print()
    
    # Özet
    print("=" * 70)
    print(" TRAIN/TEST AYRIMI TAMAMLANDI")
    print("=" * 70)
    print(f" Toplam: {len(reports)} rapor")
    print(f" Train: {len(train_reports)} rapor → {train_dir}")
    print(f" Test: {len(test_reports)} rapor → {test_dir}")
    print(f" Ayrım bilgisi: {split_info_file}")
    print()


if __name__ == "__main__":
    main()

