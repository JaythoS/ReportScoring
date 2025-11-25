"""
Chunking destekli segmentasyon - Uzun metinler için
"""
import os
import sys
import json
import time
import unicodedata
import re
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Model ve prompt yükleme
MODEL_NAME = "gemini-2.0-flash"

def load_prompt() -> str:
    """Segmentation prompt şablonunu yükle"""
    project_root = Path(__file__).resolve().parents[2]
    prompt_path = project_root / "llm" / "prompts" / "segmentation.json.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt dosyası bulunamadı: {prompt_path}")
    
    return prompt_path.read_text(encoding="utf-8")


def _extract_text(resp) -> str:
    """Gemini yanıtından metni güvenli biçimde çıkar"""
    if not resp:
        return ""
    if getattr(resp, "text", None):
        return resp.text
    try:
        parts = []
        for c in getattr(resp, "candidates", []) or []:
            for part in getattr(c, "content", {}).parts or []:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return "".join(parts)
    except Exception:
        return ""


def _repair_json(json_str: str) -> str:
    """JSON string'i onarmaya çalış (basit hataları düzelt)"""
    if not json_str:
        return json_str
    
    # Markdown temizleme
    if "```json" in json_str:
        start = json_str.find("```json") + 7
        end = json_str.find("```", start)
        if end != -1:
            json_str = json_str[start:end].strip()
    elif "```" in json_str:
        start = json_str.find("```") + 3
        end = json_str.find("```", start)
        if end != -1:
            json_str = json_str[start:end].strip()
    
    # Trailing comma temizleme (basit)
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str


def segment_text(text: str, api_key: str = None) -> str:
    """Tek chunk için segmentasyon yap (chunked olmayan kısa metinler için)"""
    api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        },
    )
    
    prompt = load_prompt().format(TEXT=text, SOURCE_LEN=len(text))
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt)
            output = _extract_text(resp).strip()
            
            if not output:
                raise RuntimeError("Boş yanıt döndü")
            
            # Model çıktısını temizle
            output = clean_model_output(output)
            
            # JSON parse et
            try:
                data = json.loads(output)
            except json.JSONDecodeError:
                # Repair dene
                repaired = _repair_json(output)
                data = json.loads(repaired)
            
            return json.dumps(data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            if "429" in str(e) or "Resource exhausted" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                else:
                    raise RuntimeError(f"Rate limit hatası: {e}")
            else:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise


# Chunking parametreleri
MAX_CHUNK_SIZE = 15000  # karakter
CHUNK_OVERLAP = 800  # Chunk'lar arası overlap (başlık kaybını önlemek için) - artırıldı
MIN_FILL_RATIO = 0.65  # Minimum chunk doluluk oranı (%65)


def split_text_into_chunks(text: str, chunk_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP, min_fill_ratio: float = MIN_FILL_RATIO) -> list:
    """Metni chunk'lara böl (başlık kaybını önlemek için akıllı bölme)
    
    İyileştirmeler:
    - Minimum doluluk eşiği (%65)
    - Geriye düşmeyi engelleme
    - Çift satır sonu (\n\n) → tek satır sonu (\n) sırasıyla yumuşak kes
    """
    chunks = []
    text_len = len(text)
    min_chunk_size = int(chunk_size * min_fill_ratio)
    
    if text_len <= chunk_size:
        return [(0, text_len, text)]
    
    start = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        original_end = end
        
        # Eğer son chunk değilse, satır sonu veya paragraf sonu bul
        if end < text_len:
            # Önce çift satır sonu (\n\n) ara
            newline_pos = text.rfind('\n\n', start, end)
            if newline_pos > start + min_chunk_size:  # Minimum doluluk eşiğini koru
                end = newline_pos + 2
            else:
                # Tek satır sonu (\n) ara
                newline_pos = text.rfind('\n', start, end)
                if newline_pos > start + min_chunk_size:
                    end = newline_pos + 1
                # Eğer minimum doluluk eşiği sağlanamazsa, orijinal end'i kullan
        
        # Minimum doluluk kontrolü
        chunk_length = end - start
        if chunk_length < min_chunk_size and end < text_len:
            # Chunk çok küçük, daha fazla al
            end = min(start + chunk_size, text_len)
        
        chunk_text = text[start:end]
        chunks.append((start, end, chunk_text))
        
        # Sonraki chunk için başlangıç (overlap ile) - GERİYE DÜŞMEYİ ENGELLE
        if end < text_len:
            # Overlap: sonraki chunk bir önceki chunk'ın sonundan overlap kadar geriye başlasın
            new_start = end - overlap
            
            # ÖNEMLİ: Geriye düşmeyi engelle - her zaman ileriye git
            prev_start = chunks[-1][0] if chunks else 0
            if new_start <= prev_start:
                # Geriye düştüyse, önceki chunk'ın sonundan 1 karakter ileri başla
                new_start = end
            else:
                # Overlap içinde yumuşak bir kesme noktası bul
                # Önce çift satır sonu, sonra tek satır sonu ara
                overlap_start = max(prev_start, new_start - overlap // 2)
                soft_break = text.rfind('\n\n', overlap_start, new_start)
                if soft_break > overlap_start:
                    new_start = soft_break + 2
                else:
                    soft_break = text.rfind('\n', overlap_start, new_start)
                    if soft_break > overlap_start:
                        new_start = soft_break + 1
            
            start = new_start
        else:
            break
    
    return chunks


def calculate_iou(start1: int, end1: int, start2: int, end2: int) -> float:
    """İki aralık arasındaki Intersection over Union (IoU) hesapla"""
    intersection_start = max(start1, start2)
    intersection_end = min(end1, end2)
    
    if intersection_end <= intersection_start:
        return 0.0
    
    intersection = intersection_end - intersection_start
    union = (end1 - start1) + (end2 - start2) - intersection
    
    if union == 0:
        return 1.0 if start1 == start2 and end1 == end2 else 0.0
    
    return intersection / union


def normalize_section_name(name: str) -> str:
    """Section name'i normalize et (karşılaştırma için)"""
    if not name:
        return ""
    # Küçük harfe çevir, fazla boşlukları temizle
    normalized = " ".join(name.lower().split())
    return normalized


def smart_dedup_sections(all_sections: list, iou_threshold_with_title: float = 0.6, iou_threshold_no_title: float = 0.8) -> list:
    """Akıllı duplicate temizleme - IoU ve başlık eşleşmesi ile
    
    Args:
        all_sections: Tüm section'ların listesi
        iou_threshold_with_title: Başlık eşleşiyorsa IoU eşiği (0.6)
        iou_threshold_no_title: Başlık yoksa IoU eşiği (0.8)
    
    Returns:
        Temizlenmiş section listesi
    """
    if not all_sections:
        return []
    
    # Önce start_idx'e göre sırala
    sorted_sections = sorted(all_sections, key=lambda x: (x.get('start_idx', 0), x.get('end_idx', 0)))
    
    unique_sections = []
    seen_ids = set()
    id_counter = {}
    
    for section in sorted_sections:
        start = section.get('start_idx', 0)
        end = section.get('end_idx', 0)
        section_name = section.get('section_name', '')
        section_id = section.get('section_id', '')
        
        # Benzersiz ID kontrolü
        if section_id in seen_ids:
            # Yeni benzersiz ID oluştur
            base_id = section_id.rsplit('_', 1)[0] if '_' in section_id else section_id
            if base_id not in id_counter:
                id_counter[base_id] = 1
            else:
                id_counter[base_id] += 1
            section_id = f"{base_id}_{id_counter[base_id]}"
            section['section_id'] = section_id
        
        seen_ids.add(section_id)
        
        # Aynı section_id'yi normalize et
        normalized_name = normalize_section_name(section_name)
        
        # Mevcut section'larla karşılaştır
        merged = False
        for existing in unique_sections:
            existing_start = existing.get('start_idx', 0)
            existing_end = existing.get('end_idx', 0)
            existing_name = existing.get('section_name', '')
            existing_normalized = normalize_section_name(existing_name)
            
            # IoU hesapla
            iou = calculate_iou(start, end, existing_start, existing_end)
            
            # Başlık eşleşmesi kontrolü
            name_match = normalized_name and existing_normalized and normalized_name == existing_normalized
            
            # Eşik belirleme
            threshold = iou_threshold_with_title if name_match else iou_threshold_no_title
            
            # Eşik aşıldıysa birleştir
            if iou >= threshold:
                # Daha uzun içeriğe sahip olanı tut
                existing_content_len = len(existing.get('content', ''))
                new_content_len = len(section.get('content', ''))
                
                if new_content_len > existing_content_len:
                    # Yeni section daha uzun, mevcut olanı güncelle
                    unique_sections.remove(existing)
                    unique_sections.append(section)
                # Aksi halde mevcut olanı tut (yeni section'ı atla)
                merged = True
                break
        
        if not merged:
            unique_sections.append(section)
    
    # Tekrar sırala
    unique_sections.sort(key=lambda x: x.get('start_idx', 0))
    
    return unique_sections


def validate_segmentation_result(sections: list, original_text: str) -> dict:
    """Mini validator - sessiz hataları erken yakala
    
    Returns:
        {
            'valid': bool,
            'errors': list,
            'warnings': list
        }
    """
    errors = []
    warnings = []
    section_ids = set()
    
    for i, section in enumerate(sections):
        start = section.get('start_idx', 0)
        end = section.get('end_idx', 0)
        section_id = section.get('section_id', '')
        
        # start_idx < end_idx kontrolü
        if start >= end:
            errors.append(f"Section {i} ({section_id}): start_idx ({start}) >= end_idx ({end})")
        
        # Sınırlar metin dışında mı?
        if start < 0:
            errors.append(f"Section {i} ({section_id}): start_idx ({start}) < 0")
        if end > len(original_text):
            errors.append(f"Section {i} ({section_id}): end_idx ({end}) > text length ({len(original_text)})")
        
        # Yinelenen section_id kontrolü
        if section_id in section_ids:
            errors.append(f"Duplicate section_id: {section_id}")
        section_ids.add(section_id)
    
    # Sıralama sonrası büyük overlap kontrolü
    sorted_sections = sorted(sections, key=lambda x: x.get('start_idx', 0))
    for i in range(len(sorted_sections) - 1):
        curr = sorted_sections[i]
        next_sec = sorted_sections[i + 1]
        
        curr_end = curr.get('end_idx', 0)
        next_start = next_sec.get('start_idx', 0)
        
        if curr_end > next_start:
            overlap = curr_end - next_start
            curr_size = curr_end - curr.get('start_idx', 0)
            overlap_ratio = overlap / curr_size if curr_size > 0 else 0
            
            if overlap_ratio > 0.3:  # %30'dan fazla overlap
                warnings.append(
                    f"Large overlap between {curr.get('section_id')} and {next_sec.get('section_id')}: "
                    f"{overlap} chars ({overlap_ratio:.1%})"
                )
    
    try:
        from fix_segmentation import summarize_rubric_coverage
        coverage = summarize_rubric_coverage(sections)
        for rubric_id, present in coverage.items():
            if not present:
                warnings.append(f"Rubric criterion {rubric_id} missing (no matching section detected)")
    except Exception:
        warnings.append("Rubric coverage summary failed")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def clean_model_output(output: str) -> str:
    """Model çıktısını temizle - Unicode normalize ve kontrol karakterleri"""
    if not output:
        return output
    
    # Unicode normalize et (NFC)
    output = unicodedata.normalize("NFC", output)
    
    # Kontrol karakterlerini temizle - JSON'da geçerli olanlar (\n, \r, \t) hariç
    # Null karakterleri ve diğer kontrol karakterleri sil
    cleaned = []
    for char in output:
        code = ord(char)
        if code == 0:
            # Null karakteri sil
            continue
        elif code < 32:
            # Sadece geçerli kontrol karakterleri bırak (\n, \r, \t)
            if char in ['\n', '\r', '\t']:
                cleaned.append(char)
            # Diğer kontrol karakterleri sil (JSON'da sorun yaratabilir)
            continue
        elif 127 <= code <= 159:
            # DEL ve diğer kontrol karakterleri sil
            continue
        else:
            cleaned.append(char)
    
    return ''.join(cleaned)


def merge_segmentations(chunk_results: list, original_text: str) -> dict:
    """Chunk sonuçlarını birleştir"""
    all_sections = []
    
    for chunk_data in chunk_results:
        chunk_start_idx = chunk_data['chunk_start']
        sections = chunk_data['sections']
        
        # Section'ların start_idx ve end_idx'lerini orijinal metne göre ayarla
        for section in sections:
            # Chunk içindeki relative pozisyonları absolute pozisyonlara çevir
            section['start_idx'] = chunk_start_idx + section.get('start_idx', 0)
            section['end_idx'] = chunk_start_idx + section.get('end_idx', 0)
            all_sections.append(section)
    
    # Akıllı duplicate temizleme (IoU ile)
    unique_sections = smart_dedup_sections(all_sections)
    
    # Parent_id'leri düzelt (chunking sonrası parent_id'ler kaybolmuş olabilir)
    try:
        fix_seg_path = Path(__file__).parent / "fix_segmentation.py"
        if fix_seg_path.exists():
            sys.path.insert(0, str(Path(__file__).parent))
            from fix_segmentation import fix_missing_parents, apply_rubric_hierarchy_fixes
            unique_sections = fix_missing_parents(unique_sections)
            unique_sections = apply_rubric_hierarchy_fixes(unique_sections)
        else:
            raise ImportError("fix_segmentation.py not found")
    except (ImportError, Exception):
        # Eğer import edilemezse, basit bir düzeltme yap
        all_ids = {s.get('section_id') for s in unique_sections}
        for i, sec in enumerate(unique_sections):
            level = sec.get('level', 1)
            parent_id = sec.get('parent_id')
            
            # Geçersiz parent_id'yi düzelt
            if parent_id and parent_id not in all_ids:
                # En yakın geçerli parent'ı bul
                for j in range(i - 1, -1, -1):
                    prev_sec = unique_sections[j]
                    if prev_sec.get('level') == level - 1:
                        sec['parent_id'] = prev_sec.get('section_id')
                        break
                else:
                    sec['parent_id'] = None
            
            # Level 2+ bölümler için parent_id kontrolü
            if level > 1 and not sec.get('parent_id'):
                for j in range(i - 1, -1, -1):
                    prev_sec = unique_sections[j]
                    if prev_sec.get('level') == level - 1:
                        sec['parent_id'] = prev_sec.get('section_id')
                        break
    
    return {
        "segmentation": {
            "sections": unique_sections
        },
        "source_metadata": {
            "total_length": len(original_text),
            "extraction_timestamp": datetime.now().isoformat(),
            "chunked": True,
            "chunk_count": len(chunk_results)
        }
    }


def segment_text_chunked(text: str, api_key: str = None) -> str:
    """Uzun metinleri chunk'lara bölerek işle"""
    api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    
    # Chunk'lara böl
    chunks = split_text_into_chunks(text)
    
    if len(chunks) == 1:
        # Tek chunk, normal segmentasyon
        return segment_text(text, api_key=api_key)
    
    print(f" Metin {len(chunks)} chunk'a bölündü (her chunk ~{MAX_CHUNK_SIZE:,} karakter)")
    print()
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        },
    )
    
    chunk_results = []
    
    # Her chunk'ı işle
    for i, (chunk_start, chunk_end, chunk_text) in enumerate(chunks, 1):
        print(f" Chunk {i}/{len(chunks)} işleniyor... (pozisyon {chunk_start:,}-{chunk_end:,})")
        
        prompt = load_prompt().format(TEXT=chunk_text, SOURCE_LEN=len(chunk_text))
        
        # Chunk'ı işle
        max_retries = 3
        output = None
        
        for attempt in range(max_retries):
            try:
                resp = model.generate_content(prompt)
                output = _extract_text(resp).strip()
                break
            except Exception as e:
                if "429" in str(e) or "Resource exhausted" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    else:
                        raise RuntimeError(f"Rate limit hatası (chunk {i})")
                else:
                    raise
        
        if not output:
            print(f"  Chunk {i} boş yanıt döndü, atlanıyor...")
            continue
        
        # Model çıktısını temizle
        output = clean_model_output(output)
        
        # JSON parse et
        try:
            data = json.loads(output)
            sections = data.get('segmentation', {}).get('sections', [])
            chunk_results.append({
                'chunk_start': chunk_start,
                'sections': sections
            })
            print(f"    {len(sections)} bölüm çıkarıldı")
        except json.JSONDecodeError as e:
            # Repair dene
            print(f"     JSON parse hatası: {e}")
            print(f"    Repair deneniyor...")
            repaired = _repair_json(output)
            try:
                data = json.loads(repaired)
                sections = data.get('segmentation', {}).get('sections', [])
                chunk_results.append({
                    'chunk_start': chunk_start,
                    'sections': sections
                })
                print(f"    {len(sections)} bölüm çıkarıldı (repair ile)")
            except json.JSONDecodeError as e2:
                print(f"    Chunk {i} repair ile de parse edilemedi: {e2}")
                print(f"    Retry ile tekrar deneniyor...")
                
                # Retry ile tekrar dene
                time.sleep(2)
                try:
                    retry_prompt = prompt + "\n\nCRITICAL: Output MUST be valid JSON. All strings must be properly escaped. No markdown, ONLY valid JSON."
                    resp2 = model.generate_content(retry_prompt)
                    output2 = _extract_text(resp2).strip()
                    
                    # Model çıktısını temizle
                    output2 = clean_model_output(output2)
                    
                    # Markdown temizleme
                    if "```json" in output2:
                        start = output2.find("```json") + 7
                        end = output2.find("```", start)
                        if end != -1:
                            output2 = output2[start:end].strip()
                    elif "```" in output2:
                        start = output2.find("```") + 3
                        end = output2.find("```", start)
                        if end != -1:
                            output2 = output2[start:end].strip()
                    
                    try:
                        data = json.loads(output2)
                        sections = data.get('segmentation', {}).get('sections', [])
                        chunk_results.append({
                            'chunk_start': chunk_start,
                            'sections': sections
                        })
                        print(f"   {len(sections)} bölüm çıkarıldı (retry ile)")
                    except:
                        # Son çare: repair ile tekrar dene
                        repaired2 = _repair_json(output2)
                        try:
                            data = json.loads(repaired2)
                            sections = data.get('segmentation', {}).get('sections', [])
                            chunk_results.append({
                                'chunk_start': chunk_start,
                                'sections': sections
                            })
                            print(f"    {len(sections)} bölüm çıkarıldı (retry + repair ile)")
                        except:
                            print(f"    Chunk {i} tamamen başarısız, atlanıyor...")
                            print(f"     Bu chunk'daki bölümler eksik kalacak!")
                except Exception as retry_error:
                    print(f"    Retry hatası: {retry_error}")
                    print(f"    Chunk {i} atlanıyor - bu chunk'daki bölümler eksik kalacak!")
        
        print()
    
    # Sonuçları birleştir
    print(" Chunk sonuçları birleştiriliyor...")
    merged = merge_segmentations(chunk_results, text)
    
    # Validasyon
    sections = merged.get('segmentation', {}).get('sections', [])
    validation = validate_segmentation_result(sections, text)
    
    if not validation['valid']:
        print("  Validasyon hataları bulundu:")
        for error in validation['errors']:
            print(f"    {error}")
    
    if validation['warnings']:
        print("  Validasyon uyarıları:")
        for warning in validation['warnings'][:5]:  # İlk 5 uyarıyı göster
            print(f"     {warning}")
        if len(validation['warnings']) > 5:
            print(f"   ... ve {len(validation['warnings']) - 5} uyarı daha")
    
    if validation['valid']:
        print(" Validasyon başarılı!")
    
    return json.dumps(merged, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Test
    sample = "Introduction\nThis is a demo.\nMethodology\nWe did X.\nResults\n...\nConclusion\nDone." * 1000
    result = segment_text_chunked(sample)
    print(result[:500])

