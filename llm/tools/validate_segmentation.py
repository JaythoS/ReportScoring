"""
Segmentation çıktısını doğrula ve sorunları tespit et
"""
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple


def validate_segmentation(json_file: Path) -> Dict:
    """Segmentation JSON'unu doğrula ve sorunları raporla"""
    data = json.loads(json_file.read_text(encoding='utf-8'))
    sections = data.get('segmentation', {}).get('sections', [])
    
    issues = {
        'duplicate_ids': [],
        'hierarchy_issues': [],
        'content_gaps': [],
        'overlaps': [],
        'missing_parents': [],
        'invalid_indices': []
    }
    
    # 1. Tekrarlanan section_id kontrolü
    section_ids = [s.get('section_id') for s in sections]
    duplicate_ids = [sid for sid, count in Counter(section_ids).items() if count > 1]
    issues['duplicate_ids'] = duplicate_ids
    
    # 2. Hiyerarşi kopuklukları
    for sec in sections:
        level = sec.get('level', 1)
        parent_id = sec.get('parent_id')
        section_id = sec.get('section_id')
        
        if level > 1 and not parent_id:
            issues['missing_parents'].append({
                'section_id': section_id,
                'level': level,
                'section_name': sec.get('section_name', '')[:50]
            })
        
        # Parent_id var ama geçersiz mi kontrol et
        if parent_id and parent_id not in section_ids:
            issues['hierarchy_issues'].append({
                'section_id': section_id,
                'invalid_parent': parent_id
            })
    
    # 3. start_idx/end_idx tutarlılığı
    sorted_sections = sorted(sections, key=lambda x: x.get('start_idx', 0))
    
    for i in range(len(sorted_sections) - 1):
        current = sorted_sections[i]
        next_sec = sorted_sections[i+1]
        current_end = current.get('end_idx', 0)
        next_start = next_sec.get('start_idx', 0)
        
        if current_end > next_start:
            issues['overlaps'].append({
                'section1': current.get('section_id'),
                'section2': next_sec.get('section_id'),
                'overlap_size': current_end - next_start
            })
        elif next_start - current_end > 10:
            issues['content_gaps'].append({
                'section1': current.get('section_id'),
                'section2': next_sec.get('section_id'),
                'gap_size': next_start - current_end
            })
    
    # 4. İçerik kesikleri (sadece sayfa numarası)
    for sec in sections:
        content = sec.get('content', '').strip()
        if len(content) < 10 and content.isdigit():
            issues['content_gaps'].append({
                'section_id': sec.get('section_id'),
                'issue': 'Sadece sayfa numarası',
                'content': content
            })
    
    return {
        'issues': issues,
        'total_sections': len(sections),
        'summary': {
            'duplicate_ids_count': len(duplicate_ids),
            'missing_parents_count': len(issues['missing_parents']),
            'overlaps_count': len(issues['overlaps']),
            'gaps_count': len(issues['content_gaps'])
        }
    }


def print_validation_report(validation_result: Dict):
    """Doğrulama raporunu yazdır"""
    issues = validation_result['issues']
    summary = validation_result['summary']
    
    print("=" * 70)
    print("📋 SEGMENTATION DOĞRULAMA RAPORU")
    print("=" * 70)
    print()
    print(f"📊 Toplam bölüm: {validation_result['total_sections']}")
    print()
    
    # 1. Tekrarlanan ID'ler
    if summary['duplicate_ids_count'] > 0:
        print(f"❌ 1. TEKRARLANAN SECTION_ID'LER: {summary['duplicate_ids_count']}")
        for sid in issues['duplicate_ids'][:10]:
            print(f"   - {sid}")
    else:
        print("✅ 1. TEKRARLANAN ID: Yok")
    print()
    
    # 2. Eksik parent_id
    if summary['missing_parents_count'] > 0:
        print(f"❌ 2. EKSİK PARENT_ID: {summary['missing_parents_count']}")
        for item in issues['missing_parents'][:10]:
            print(f"   - [{item['section_id']}] Level {item['level']}: {item['section_name']}")
    else:
        print("✅ 2. PARENT_ID: Tüm alt bölümlerde var")
    print()
    
    # 3. Overlaps
    if summary['overlaps_count'] > 0:
        print(f"❌ 3. BÖLÜM OVERLAP'LERİ: {summary['overlaps_count']}")
        for item in issues['overlaps'][:10]:
            print(f"   - {item['section1']} ve {item['section2']} arasında {item['overlap_size']} karakter overlap")
    else:
        print("✅ 3. OVERLAP: Yok")
    print()
    
    # 4. Gaps
    if summary['gaps_count'] > 0:
        print(f"⚠️  4. İÇERİK BOŞLUKLARI/KESİKLERİ: {summary['gaps_count']}")
        for item in issues['content_gaps'][:10]:
            if 'gap_size' in item:
                print(f"   - {item['section1']} ve {item['section2']} arasında {item['gap_size']} karakter boşluk")
            else:
                print(f"   - [{item['section_id']}]: {item.get('issue', '')} - '{item.get('content', '')}'")
    else:
        print("✅ 4. BOŞLUK/KESİK: Yok")
    print()
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
    else:
        # En son Doğuş Teknoloji dosyasını bul
        json_file = sorted(
            Path('outputs/segmentations').glob('Dog*'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[0]
    
    print(f"📄 Dosya: {json_file.name}")
    print()
    
    result = validate_segmentation(json_file)
    print_validation_report(result)



