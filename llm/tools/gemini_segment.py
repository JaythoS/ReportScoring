import os
import json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai

MODEL_NAME = "gemini-2.0-flash"  # veya "gemini-2.5-flash", "gemini-flash-latest" kullanılabilir

def load_prompt() -> str:
    """LLM prompt şablonunu yükle (JSON formatı)"""
    p = Path(__file__).resolve().parents[1] / "prompts" / "segmentation.json.txt"
    if not p.exists():
        raise FileNotFoundError(f"Prompt dosyası bulunamadı: {p}")
    return p.read_text(encoding="utf-8")

def _extract_text(resp) -> str:
    """Gemini yanıtından metni güvenli biçimde çıkar (text boşsa candidates/parts’a bak)."""
    if not resp:
        return ""
    if getattr(resp, "text", None):
        return resp.text
    # Bazı durumlarda çıktı parçalar halinde gelir
    try:
        parts = []
        for c in getattr(resp, "candidates", []) or []:
            for part in getattr(c, "content", {}).parts or []:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return "".join(parts)
    except Exception:
        return ""

def segment_text(text: str, api_key: str = None) -> str:
    api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0,
            # JSON üretimi için MIME türünü belirt (XML desteklenmiyor)
            "response_mime_type": "application/json"
        },
        # İstersen güvenlik eşiğini biraz gevşetebilirsin
        safety_settings={
            # örnek: her kategoriyi "BLOCK_NONE" yaparsan boş dönme ihtimali azalır
            # "HARASSMENT": "BLOCK_NONE",
            # "HATE_SPEECH": "BLOCK_NONE",
            # "SEXUAL": "BLOCK_NONE",
            # "DANGEROUS": "BLOCK_NONE",
        },
    )

    prompt = load_prompt().format(TEXT=text, SOURCE_LEN=len(text))
    
    # Rate limit kontrolü için retry mekanizması
    max_retries = 3
    retry_delay = 5  # saniye
    
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt)
            output = _extract_text(resp).strip()
            break
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"⚠️  Rate limit hatası. {wait_time} saniye bekleniyor... (Deneme {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(
                        f"API rate limit aşıldı ({max_retries} deneme başarısız).\n"
                        "Lütfen 5-10 dakika bekleyip tekrar deneyin.\n"
                        "Alternatif: Metni daha küçük parçalara bölerek işleyin."
                    )
            else:
                raise
    
    if not output:
        raise RuntimeError("LLM'den çıktı alınamadı.")

    # JSON çıktıyı kontrol et
    if not output:
        print("⚠️  Model boş yanıt döndürdü.")
        if hasattr(resp, "prompt_feedback"):
            print("Prompt feedback:", resp.prompt_feedback)
        return ""
    
    # JSON temizleme: Markdown kod blokları varsa kaldır
    if "```json" in output:
        start = output.find("```json") + 7
        end = output.find("```", start)
        if end != -1:
            output = output[start:end].strip()
    elif "```" in output:
        start = output.find("```") + 3
        end = output.find("```", start)
        if end != -1:
            output = output[start:end].strip()
    
    # JSON geçerli mi kontrol et
    try:
        import json
        # JSON parse test
        parsed = json.loads(output)
        # Başarılıysa pretty print ile döndür
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        # JSON geçersizse, tekrar dene (daha sert talimatla)
        print(f"⚠️  JSON parse hatası: {e}")
        print("🔄 Düzeltilmiş prompt ile tekrar deneniyor...")
        
        # Rate limit kontrolü
        import time
        time.sleep(2)  # Rate limit için bekle
        
        try:
            retry_prompt = (
                prompt
                + "\n\nCRITICAL: Output MUST be valid JSON. "
                "All strings must be properly escaped. "
                "Newlines in content must be \\n, quotes must be \\\". "
                "No markdown, no explanations, ONLY valid JSON."
            )
            resp2 = model.generate_content(retry_prompt)
            output = _extract_text(resp2).strip()
        except Exception as retry_error:
            if "429" in str(retry_error) or "Resource exhausted" in str(retry_error):
                raise RuntimeError(
                    "API rate limit aşıldı. Lütfen birkaç dakika bekleyip tekrar deneyin.\n"
                    "Alternatif: Metni daha küçük parçalara bölerek işleyin."
                )
            raise
        
        # Temizleme tekrar yap
        if "```json" in output:
            start = output.find("```json") + 7
            end = output.find("```", start)
            if end != -1:
                output = output[start:end].strip()
        elif "```" in output:
            start = output.find("```") + 3
            end = output.find("```", start)
            if end != -1:
                output = output[start:end].strip()
        
        # Son deneme
        try:
            parsed = json.loads(output)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError as e2:
            print(f"❌ JSON parse hatası devam ediyor: {e2}")
            print(f"🔄 JSON'u tamamlamaya çalışılıyor...")
            
            # JSON'u tamamlamaya çalış
            repaired = _repair_json(output)
            try:
                parsed = json.loads(repaired)
                print(f"✅ JSON tamamlandı ve parse edildi!")
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            except json.JSONDecodeError as e3:
                print(f"⚠️  JSON tamamlama başarısız: {e3}")
                print(f"İlk 500 karakter: {output[:500]}")
                # Yine de çıktıyı döndür (kullanıcı manuel düzeltebilir)
                return output
    
    return output


def _repair_json(incomplete_json: str) -> str:
    """Yarım kalmış JSON'u tamamlamaya çalış"""
    import re
    import unicodedata
    
    output = incomplete_json.strip()
    
    # Unicode normalize et
    output = unicodedata.normalize("NFC", output)
    
    # Kontrol karakterlerini temizle (null karakterleri sil)
    output = output.replace('\x00', '')
    
    # 1. "parent" gibi yarım kalan key'leri düzelt
    output = re.sub(r'"parent"\s*$', '"parent_id": null', output, flags=re.MULTILINE)
    
    # 2. Kapanmamış content string'lerini kapat
    # Son satırda kapanmamış tırnak var mı?
    lines = output.split('\n')
    if lines:
        # Son satırı kontrol et
        last_line = lines[-1].strip()
        
        # Eğer son satır "content": ile başlayan bir satırdan sonra geliyorsa
        # ve tırnak ile bitmiyorsa, kapat
        content_started = False
        for i in range(len(lines) - 1, max(0, len(lines) - 20), -1):
            if '"content":' in lines[i]:
                content_started = True
                break
        
        if content_started:
            # Son satırda tırnak kontrolü
            # Eğer son satır tırnak ile bitmiyorsa ve içinde tırnak yoksa, kapat
            if not last_line.endswith('"') and not last_line.endswith('",') and not last_line.endswith('"}'):
                # Son satırı kapat
                lines[-1] = lines[-1].rstrip() + '"'
                # Eğer section'un sonu değilse virgül ekle
                if not lines[-1].strip().endswith('",'):
                    lines[-1] = lines[-1].rstrip().rstrip(',') + '",'
                output = '\n'.join(lines)
    
    # 3. Eksik alanları ekle (start_idx, end_idx, level, parent_id)
    # Eğer son section'da bunlar yoksa ekle
    if '"section_id":' in output:
        # Son section'ı bul
        last_section_start = output.rfind('{')
        if last_section_start > 0:
            last_section = output[last_section_start:]
            # Eksik alanları kontrol et ve ekle
            if '"start_idx"' not in last_section:
                # Son content'ten sonra ekle
                if '"content":' in last_section:
                    content_end = last_section.rfind('",')
                    if content_end > 0:
                        indent = '        '
                        last_section = last_section[:content_end+2] + f',\n{indent}"start_idx": 0,\n{indent}"end_idx": 0,\n{indent}"level": 1,\n{indent}"parent_id": null'
                        output = output[:last_section_start] + last_section
    
    # 4. Kapanmamış section object'lerini kapat
    output_stripped = output.rstrip()
    if not output_stripped.endswith('}') and not output_stripped.endswith(']'):
        open_braces = output.count('{')
        close_braces = output.count('}')
        missing_braces = open_braces - close_braces
        
        if missing_braces > 0:
            # Son satırın indent'ini al
            last_line = output.split('\n')[-1] if output.split('\n') else ''
            indent_level = (len(last_line) - len(last_line.lstrip())) // 2
            
            # Section object'ini kapat
            if missing_braces >= 1:
                output += '\n' + '  ' * indent_level + '}'
            
            # Sections array'ini kapat
            if missing_braces >= 2:
                output += '\n    ]'
            
            # Segmentation object'ini kapat
            if missing_braces >= 3:
                output += '\n  }'
    
    # 5. sections array'ini kapat (eğer kapanmamışsa)
    if output.count('[') > output.count(']'):
        if not output.rstrip().endswith(']'):
            output += '\n    ]'
    
    # 6. segmentation object'ini kapat (eğer kapanmamışsa)
    if '"segmentation"' in output:
        if output.count('{') > output.count('}'):
            if not output.rstrip().endswith('  }'):
                output += '\n  }'
    
    # 7. Ana object'i kapat
    if output.count('{') > output.count('}'):
        output += '\n}'
    
    # 8. Metadata ekle (eğer yoksa)
    if '"source_metadata"' not in output:
        output = output.rstrip()
        if output.endswith('}'):
            output = output[:-1].rstrip()
            if not output.endswith(','):
                output += ','
            output += '\n  "source_metadata": {\n'
            output += '    "total_length": 0,\n'
            output += '    "extraction_timestamp": "' + datetime.now().isoformat() + '"\n'
            output += '  }\n}'
    
    return output


if __name__ == "__main__":
    sample = "Introduction\nThis is a demo.\nMethodology\nWe did X.\nResults\n...\nConclusion\nDone."
    json_output = segment_text(sample)
    # repr ile görünmez karakterleri de görebilelim
    print(repr(json_output))
    # Aynı zamanda dosyaya da yazalım
    out = Path(__file__).with_name("last_output.json")
    out.write_text(json_output, encoding="utf-8")
    print(f"📝 JSON {out.name} dosyasına kaydedildi.")