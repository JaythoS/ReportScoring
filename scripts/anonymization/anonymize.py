#!/usr/bin/env python3
"""
Anonimleştirme Scripti

Staj raporlarında bulunan kişisel verileri anonimleştirir (GDPR/KVKK uyumluluğu için).
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Proje root'unu path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


# Regex Pattern'leri (önem sırasına göre - önce spesifik olanlar)
PATTERNS = {
    # Önce email ve URL gibi kesin pattern'ler
    "EMAIL": {
        "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "replacement": "[EMAIL]",
        "description": "E-posta adresi",
        "priority": 1
    },
    "URL": {
        "pattern": r'https?://[^\s<>"]+',
        "replacement": "[URL]",
        "description": "Web sitesi URL'si",
        "priority": 1
    },
    # Telefon numarası (Türk formatı)
    "PHONE": {
        "pattern": r'\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|\+90\s?\d{10}|\d{10}(?=\s|$)',
        "replacement": "[PHONE]",
        "description": "Telefon numarası",
        "priority": 2
    },
    # Öğrenci ID (9 haneli, bağımsız)
    "STUDENT_ID": {
        "pattern": r'\b\d{9}\b(?![0-9])',
        "replacement": "[STUDENT_ID]",
        "description": "9 haneli öğrenci numarası",
        "priority": 2
    },
    # Şirket adı (bağlam bazlı - daha güvenli)
    "COMPANY_NAME": {
        "pattern": r'Company Name:\s*([A-ZÇĞİÖŞÜ][^\n]{2,50})',
        "replacement": "Company Name: [COMPANY_NAME]",
        "description": "Şirket adı (bağlam bazlı)",
        "priority": 3
    },
    # Adres (daha spesifik)
    "ADDRESS": {
        "pattern": r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+(Mah\.|Sok\.|Cad\.|Bulvarı|Caddesi|Sokak|Mahallesi))\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+)?(No:\s?\d+)?\s*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+/[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?',
        "replacement": "[ADDRESS]",
        "description": "Adres bilgisi",
        "priority": 3
    },
    # Öğrenci ismi (cover sayfasında - Summer Practice Report'dan sonra gelen)
    "STUDENT_NAME_COVER": {
        # Cover sayfası formatı: "Summer Practice Report\n[İsim]\n[ID]"
        "pattern": r'(Summer Practice Report|Practice Report)\s*\n\s*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s*\n',
        "replacement": r'\1\n[STUDENT_NAME]\n',
        "description": "Cover sayfasında öğrenci adı",
        "priority": 3
    },
    # Supervisor ismi (bağlam bazlı)
    "SUPERVISOR_NAME": {
        "pattern": r'(supervisor|Supervisor|mentor|Mentor|müdür|Müdür)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)',
        "replacement": r'\1 [SUPERVISOR_NAME]',
        "description": "Supervisor adı",
        "priority": 4
    },
    # Üniversite adı (bağlam bazlı)
    "UNIVERSITY_NAME": {
        "pattern": r'(MEF|Boğaziçi|İTÜ|ODTÜ|Bilkent)\s+University',
        "replacement": "[UNIVERSITY_NAME]",
        "description": "Üniversite adı",
        "priority": 4
    }
}


class Anonymizer:
    """Anonimleştirme sınıfı"""
    
    def __init__(self, patterns: Dict = None):
        """
        Anonimleştirici oluştur
        
        Args:
            patterns: Regex pattern'leri (varsayılan: PATTERNS)
        """
        self.patterns = patterns or PATTERNS
        self.mappings = defaultdict(dict)
        self.statistics = {
            "total_replacements": 0,
            "patterns_used": 0,
            "pattern_counts": defaultdict(int)
        }
    
    def anonymize_text(self, text: str, report_id: str = "unknown") -> Tuple[str, Dict]:
        """
        Metni anonimleştir
        
        Args:
            text: Anonimleştirilecek metin
            report_id: Rapor ID'si (mapping için)
        
        Returns:
            (anonimleştirilmiş_metin, mapping_dict) tuple
        """
        anonymized_text = text
        entity_counter = defaultdict(int)
        
        # Pattern'leri priority'ye göre sırala (önem sırasına göre)
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1].get("priority", 999)
        )
        
        # Her pattern için anonimleştirme yap
        for pattern_name, pattern_info in sorted_patterns:
            pattern = pattern_info["pattern"]
            replacement_template = pattern_info["replacement"]
            
            # Pattern'i compile et
            compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            # Tüm eşleşmeleri bul (ters sırada, böylece değişiklikler indeksleri bozmaz)
            matches = list(compiled_pattern.finditer(anonymized_text))
            matches.reverse()  # Son eşleşmeden başla
            
            for match in matches:
                entity_counter[pattern_name] += 1
                original = match.group(0)
                
                # Eğer replacement template'de group referansları varsa (örn: \1)
                if '\\' in replacement_template:
                    # Group replacement yap
                    replacement = match.expand(replacement_template)
                    # Entity ID'yi ekle
                    entity_id = f"{pattern_name}_{entity_counter[pattern_name]:03d}"
                    replacement = replacement.replace(f"[{pattern_name}]", f"[{entity_id}]")
                else:
                    # Basit replacement
                    entity_id = f"{pattern_name}_{entity_counter[pattern_name]:03d}"
                    replacement = replacement_template.replace(f"[{pattern_name}]", f"[{entity_id}]")
                
                # Mapping'e ekle (sadece orijinal entity değeri)
                # Group-based pattern'lerde sadece entity değerini al
                if pattern_name in ["STUDENT_NAME_COVER", "SUPERVISOR_NAME"] and len(match.groups()) >= 2:
                    entity_value = match.group(2)  # İkinci group (isim)
                elif pattern_name == "COMPANY_NAME" and len(match.groups()) >= 1:
                    entity_value = match.group(1).strip()  # İlk group (şirket adı)
                else:
                    entity_value = original
                
                if entity_value not in self.mappings[pattern_name]:
                    self.mappings[pattern_name][entity_value] = {
                        "anonymized": f"[{entity_id}]",
                        "pattern": pattern_name,
                        "count": 0,
                        "original_full": original
                    }
                
                self.mappings[pattern_name][entity_value]["count"] += 1
                self.statistics["pattern_counts"][pattern_name] += 1
                
                # Metni değiştir (sadece bir kez, eşleşme pozisyonunda)
                start, end = match.span()
                anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
        
        # İstatistikleri güncelle
        self.statistics["total_replacements"] = sum(self.statistics["pattern_counts"].values())
        self.statistics["patterns_used"] = len([p for p in self.statistics["pattern_counts"] if self.statistics["pattern_counts"][p] > 0])
        
        # Mapping dict'i oluştur
        mapping_dict = self._create_mapping_dict(report_id)
        
        return anonymized_text, mapping_dict
    
    def _create_mapping_dict(self, report_id: str) -> Dict:
        """Mapping dictionary oluştur"""
        mappings = {}
        for pattern_name, entities in self.mappings.items():
            for original, info in entities.items():
                mappings[original] = {
                    "anonymized": info["anonymized"],
                    "pattern": info["pattern"],
                    "count": info["count"]
                }
        
        return {
            "report_id": report_id,
            "anonymization_timestamp": datetime.now().isoformat(),
            "mappings": mappings,
            "statistics": {
                "total_replacements": self.statistics["total_replacements"],
                "patterns_used": self.statistics["patterns_used"],
                "pattern_counts": dict(self.statistics["pattern_counts"])
            }
        }
    
    def save_mapping(self, mapping_dict: Dict, output_path: Path):
        """Mapping dosyasını kaydet"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(mapping_dict, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


def anonymize_file(input_path: Path, output_path: Path, mapping_path: Optional[Path] = None, report_id: str = None) -> Dict:
    """
    Dosyayı anonimleştir
    
    Args:
        input_path: Girdi dosyası yolu
        output_path: Çıktı dosyası yolu
        mapping_path: Mapping dosyası yolu (opsiyonel)
        report_id: Rapor ID'si (opsiyonel)
    
    Returns:
        Mapping dictionary
    """
    # Report ID'yi belirle
    if not report_id:
        report_id = input_path.stem.replace("_anonymized", "")
    
    # Metni oku
    text = input_path.read_text(encoding='utf-8')
    
    # Anonimleştir
    anonymizer = Anonymizer()
    anonymized_text, mapping_dict = anonymizer.anonymize_text(text, report_id)
    
    # Çıktı dosyasını kaydet
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(anonymized_text, encoding='utf-8')
    
    # Mapping dosyasını kaydet
    if mapping_path:
        anonymizer.save_mapping(mapping_dict, mapping_path)
    
    return mapping_dict


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Staj raporlarını anonimleştir (GDPR/KVKK uyumluluğu)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Girdi dosyası yolu (metin dosyası)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Çıktı dosyası yolu (anonimleştirilmiş metin)"
    )
    
    parser.add_argument(
        "--mapping",
        type=str,
        default=None,
        help="Mapping dosyası yolu (opsiyonel, reversible anonimleştirme için)"
    )
    
    parser.add_argument(
        "--report-id",
        type=str,
        default=None,
        help="Rapor ID'si (opsiyonel, mapping için)"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch işleme modu (tüm dosyaları işle)"
    )
    
    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Girdi klasörü (batch modu için)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Çıktı klasörü (batch modu için)"
    )
    
    args = parser.parse_args()
    
    # Batch modu
    if args.batch:
        if not args.input_dir or not args.output_dir:
            print("❌ Batch modu için --input-dir ve --output-dir gerekli")
            sys.exit(1)
        
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        
        # Tüm dosyaları işle
        text_files = list(input_dir.glob("*.txt"))
        
        print("=" * 70)
        print("BATCH ANONİMLEŞTİRME")
        print("=" * 70)
        print(f"📁 Girdi klasörü: {input_dir}")
        print(f"📁 Çıktı klasörü: {output_dir}")
        print(f"📄 Toplam dosya: {len(text_files)}")
        print()
        
        for i, input_file in enumerate(text_files, 1):
            report_id = input_file.stem
            output_file = output_dir / f"{report_id}_anonymized.txt"
            mapping_file = output_dir.parent / "anonymization_mappings" / f"{report_id}_mapping.json" if args.mapping else None
            
            print(f"[{i}/{len(text_files)}] İşleniyor: {input_file.name}")
            
            try:
                mapping_dict = anonymize_file(input_file, output_file, mapping_file, report_id)
                print(f"  ✅ Anonimleştirildi: {output_file.name}")
                print(f"  📊 Değiştirme sayısı: {mapping_dict['statistics']['total_replacements']}")
            except Exception as e:
                print(f"  ❌ Hata: {e}")
        
        print()
        print("✅ Batch işleme tamamlandı!")
        return
    
    # Tek dosya modu
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Girdi dosyası bulunamadı: {input_path}")
        sys.exit(1)
    
    output_path = Path(args.output)
    mapping_path = Path(args.mapping) if args.mapping else None
    
    print("=" * 70)
    print("ANONİMLEŞTİRME")
    print("=" * 70)
    print(f"📄 Girdi: {input_path}")
    print(f"📄 Çıktı: {output_path}")
    if mapping_path:
        print(f"📄 Mapping: {mapping_path}")
    print()
    
    # Anonimleştir
    mapping_dict = anonymize_file(input_path, output_path, mapping_path, args.report_id)
    
    # Sonuçları göster
    print("✅ Anonimleştirme tamamlandı!")
    print()
    print("📊 İstatistikler:")
    print(f"   Toplam değiştirme: {mapping_dict['statistics']['total_replacements']}")
    print(f"   Kullanılan pattern'ler: {mapping_dict['statistics']['patterns_used']}")
    print()
    print("📋 Pattern Dağılımı:")
    for pattern, count in mapping_dict['statistics']['pattern_counts'].items():
        print(f"   {pattern}: {count}")
    print()
    
    if mapping_path:
        print(f"💾 Mapping dosyası kaydedildi: {mapping_path}")


if __name__ == "__main__":
    main()

