"""
Segment Scoring Module
Cover ve Executive Summary segmentleri için LLM tabanlı puanlama sistemi.
Rubrik kriterlerine göre puanlama yapar.
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai

MODEL_NAME = "gemini-2.0-flash"


def load_cover_prompt() -> str:
    """Cover scoring için LLM prompt şablonunu yükle"""
    project_root = Path(__file__).resolve().parents[2]
    prompt_path = project_root / "llm" / "prompts" / "cover_scoring.json.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt dosyası bulunamadı: {prompt_path}")
    
    return prompt_path.read_text(encoding="utf-8")


def load_executive_prompt() -> str:
    """Executive Summary scoring için LLM prompt şablonunu yükle"""
    project_root = Path(__file__).resolve().parents[2]
    prompt_path = project_root / "llm" / "prompts" / "executive_scoring.json.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt dosyası bulunamadı: {prompt_path}")
    
    return prompt_path.read_text(encoding="utf-8")


def find_cover_segment(segmentation_json: Dict) -> Optional[Dict]:
    """
    Segmentasyon JSON'dan cover segmentini bul.
    Öncelik: section_id == 'cover_1', yoksa level == 1 olan ilk segment.
    
    Args:
        segmentation_json: Segmentasyon JSON dict'i
        
    Returns:
        Cover segment dict'i veya None
    """
    sections = segmentation_json.get("segmentation", {}).get("sections", [])
    
    if not sections:
        return None
    
    # Önce cover_1'i ara
    for section in sections:
        if section.get("section_id") == "cover_1":
            return section
    
    # Yoksa section_name'de "cover" geçen level 1 segmenti ara
    for section in sections:
        section_name = (section.get("section_name", "") or "").lower()
        if "cover" in section_name and section.get("level") == 1:
            return section
    
    # Hiçbiri yoksa level == 1 olan ilk segmenti al (genellikle cover)
    for section in sections:
        if section.get("level") == 1:
            return section
    
    return None


def find_executive_summary_segment(segmentation_json: Dict) -> Optional[Dict]:
    """
    Segmentasyon JSON'dan Executive Summary segmentini bul.
    
    Args:
        segmentation_json: Segmentasyon JSON dict'i
        
    Returns:
        Executive Summary segment dict'i veya None
    """
    sections = segmentation_json.get("segmentation", {}).get("sections", [])
    
    if not sections:
        return None
    
    # Executive Summary'yi ara
    for section in sections:
        section_name = (section.get("section_name", "") or "").lower()
        section_id = (section.get("section_id", "") or "").lower()
        
        # section_id'de executive_summary geçiyorsa
        if "executive_summary" in section_id or "executive" in section_id:
            return section
        
        # section_name'de executive summary geçiyorsa
        if "executive summary" in section_name and section.get("level") == 1:
            return section
    
    return None


def _call_llm_for_scoring(prompt_template: str, segment: Dict, api_key: str = None) -> Dict:
    """
    LLM'i çağırarak segment puanlaması yap (ortak fonksiyon).
    
    Args:
        prompt_template: Prompt şablonu
        segment: Segment dict'i
        api_key: Gemini API key (opsiyonel)
        
    Returns:
        Puanlama sonucu dict'i
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        },
        safety_settings={}
    )
    
    # Prompt'u formatla
    prompt = prompt_template.format(
        SECTION_NAME=segment.get("section_name", ""),
        CONTENT=segment.get("content", "")
    )
    
    # LLM'den puanlama al
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt)
            output_text = _extract_text(resp).strip()
            
            # JSON temizleme
            if "```json" in output_text:
                start = output_text.find("```json") + 7
                end = output_text.find("```", start)
                if end != -1:
                    output_text = output_text[start:end].strip()
            elif "```" in output_text:
                start = output_text.find("```") + 3
                end = output_text.find("```", start)
                if end != -1:
                    output_text = output_text[start:end].strip()
            
            # JSON parse
            result = json.loads(output_text)
            
            # En azından score alanı olmalı
            if "score" not in result:
                raise ValueError("LLM çıktısında 'score' alanı bulunamadı")
            
            return result
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            raise RuntimeError(f"JSON parse hatası: {e}\nÇıktı: {output_text[:500]}")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                if attempt < max_retries - 1:
                    import time
                    wait_time = retry_delay * (attempt + 1)
                    print(f"⚠️  Rate limit hatası. {wait_time} saniye bekleniyor...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError("API rate limit aşıldı. Lütfen birkaç dakika bekleyip tekrar deneyin.")
            raise
    
    raise RuntimeError("LLM'den geçerli çıktı alınamadı.")


def score_cover_segment(segment: Dict, api_key: str = None) -> Dict:
    """
    Cover segmentini rubrik kriterlerine göre puanla.
    
    Args:
        segment: Segment dict'i (section_id, section_name, content, vb.)
        api_key: Gemini API key (opsiyonel, env'den alınır)
        
    Returns:
        {
            "score": float,  # Toplam puan (0-10)
            "feedback": str,  # Detaylı geri bildirim
            "criteria": {
                "title_accuracy": float,  # Başlık doğruluğu (0-10)
                "format": float,          # Biçim (0-10)
                "completeness": float,    # Bilgi tamlığı (0-10)
                "date_name_presence": float  # Tarih/isim varlığı (0-10)
            }
        }
    """
    prompt_template = load_cover_prompt()
    return _call_llm_for_scoring(prompt_template, segment, api_key)


def score_executive_summary(segment: Dict, api_key: str = None) -> Dict:
    """
    Executive Summary segmentini rubrik kriterlerine göre puanla.
    
    Args:
        segment: Segment dict'i (section_id, section_name, content, vb.)
        api_key: Gemini API key (opsiyonel, env'den alınır)
        
    Returns:
        {
            "score": int,  # Rubrik seviyesi (0,20,...,100)
            "rationale": str,
            "evidence_specificity": int,
            "fine": {...},
            "criteria": {
                "executive_summary_b1": int
            }
        }
    """
    prompt_template = load_executive_prompt()
    raw_result = _call_llm_for_scoring(prompt_template, segment, api_key)
    
    rubric_score = int(raw_result.get("score", 0))
    score_0_10 = rubric_score / 10.0
    rationale = raw_result.get("rationale", "")
    fine = raw_result.get("fine", {})
    evidence_specificity = raw_result.get("evidence_specificity")
    
    # Eski çağıranlar için geri uyumluluk: criteria dict'i tek değerle doldur
    result = {
        "score": score_0_10,
        "rubric_score": rubric_score,
        "rationale": rationale,
        "fine": fine,
        "evidence_specificity": evidence_specificity,
        "feedback": rationale,
        "criteria": {
            "executive_summary_b1": score_0_10
        }
    }
    return result


# Geriye dönük uyumluluk için eski fonksiyon adları
def find_first_segment(segmentation_json: Dict) -> Optional[Dict]:
    """Geriye dönük uyumluluk için - find_cover_segment'i çağırır"""
    return find_cover_segment(segmentation_json)


def score_segment(segment: Dict, api_key: str = None) -> Dict:
    """Geriye dönük uyumluluk için - score_cover_segment'i çağırır"""
    return score_cover_segment(segment, api_key)


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


def test_multiple_reports(segmentation_files: List[Path], output_csv: Path = None) -> List[Dict]:
    """
    Birden fazla segmentation JSON dosyasını test et ve sonuçları CSV'ye kaydet.
    
    Args:
        segmentation_files: Test edilecek segmentation JSON dosya yolları
        output_csv: CSV çıktı dosyası yolu (opsiyonel)
        
    Returns:
        Test sonuçları listesi
    """
    results = []
    
    for seg_file in segmentation_files:
        print(f"\n İşleniyor: {seg_file.name}")
        
        try:
            # JSON'u yükle
            with open(seg_file, 'r', encoding='utf-8') as f:
                seg_data = json.load(f)
            
            # İlk segmenti bul
            first_segment = find_first_segment(seg_data)
            if not first_segment:
                print(f"    İlk segment bulunamadı, atlanıyor.")
                continue
            
            print(f"  Segment bulundu: {first_segment.get('section_id', 'unknown')}")
            
            # Puanla
            score_result = score_segment(first_segment)
            
            # Sonuçları kaydet
            result = {
                "file_name": seg_file.name,
                "section_id": first_segment.get("section_id", ""),
                "section_name": (first_segment.get("section_name", "") or "")[:100],  # İlk 100 karakter
                "total_score": score_result.get("score", 0.0),
                "title_accuracy": score_result.get("criteria", {}).get("title_accuracy", 0.0),
                "format": score_result.get("criteria", {}).get("format", 0.0),
                "completeness": score_result.get("criteria", {}).get("completeness", 0.0),
                "date_name_presence": score_result.get("criteria", {}).get("date_name_presence", 0.0),
                "feedback": score_result.get("feedback", "")[:500],  # İlk 500 karakter
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(result)
            
            print(f"   Toplam Puan: {result['total_score']:.2f}/10")
            print(f"     - Başlık Doğruluğu: {result['title_accuracy']:.2f}/10")
            print(f"     - Biçim: {result['format']:.2f}/10")
            print(f"     - Bilgi Tamlığı: {result['completeness']:.2f}/10")
            print(f"     - Tarih/İsim Varlığı: {result['date_name_presence']:.2f}/10")
            
        except Exception as e:
            print(f"   Hata: {e}")
            results.append({
                "file_name": seg_file.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # CSV'ye kaydet
    if output_csv and results:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        # CSV başlıkları
        fieldnames = [
            "file_name", "section_id", "section_name", "total_score",
            "title_accuracy", "format", "completeness", "date_name_presence",
            "feedback", "timestamp"
        ]
        
        # CSV'ye append (mevcut dosyayı oku ve yeni sonuçları ekle)
        file_exists = output_csv.exists()
        existing_results = []
        if file_exists:
            try:
                with open(output_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_results = list(reader)
            except Exception:
                existing_results = []
        
        # Tüm sonuçları birleştir (mevcut + yeni)
        all_results = existing_results + results
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n Sonuçlar CSV'ye kaydedildi: {output_csv}")
        
        # JSON'a da kaydet
        output_json = output_csv.parent / (output_csv.stem + ".json")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "cover_scores": all_results,
                "total_count": len(all_results),
                "last_updated": all_results[-1]["timestamp"] if all_results else None
            }, f, ensure_ascii=False, indent=2)
        
        print(f" Sonuçlar JSON'a kaydedildi: {output_json}")
        
        # Ortalama istatistikleri göster
        valid_results = [r for r in all_results if "error" not in r and "total_score" in r]
        if valid_results:
            # Sayısal değerlere dönüştür
            for r in valid_results:
                if isinstance(r.get("total_score"), str):
                    r["total_score"] = float(r["total_score"])
            avg_score = sum(r["total_score"] for r in valid_results) / len(valid_results)
            print(f"\n Ortalama Toplam Puan: {avg_score:.2f}/10")
            print(f"   Test edilen dosya sayısı: {len(valid_results)}")
    
    return results


if __name__ == "__main__":
    # Test için 3 örnek segmentation JSON dosyasını bul
    project_root = Path(__file__).resolve().parents[2]
    outputs_dir = project_root / "outputs" / "segmentations"
    
    # .fixed.json dosyalarını bul (post-processing sonrası)
    fixed_files = sorted(outputs_dir.glob("*.fixed.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if len(fixed_files) == 0:
        print(f"  Segmentation dosyası bulunamadı.")
        print(f"   {outputs_dir} klasöründe .fixed.json dosyası olmalı.")
    else:
        # Mevcut dosyaları al (en fazla 3)
        test_files = fixed_files[:min(3, len(fixed_files))]
        print(f" Test edilecek dosyalar:")
        for f in test_files:
            print(f"   - {f.name}")
        
        # CSV çıktı yolu
        csv_output = project_root / "outputs" / "cover_scores.csv"
        
        # Test çalıştır
        test_multiple_reports(test_files, csv_output)

