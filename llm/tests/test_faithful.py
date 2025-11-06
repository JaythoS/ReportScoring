"""
Faithful Extraction Test Suite
LLM bölümleme çıktılarının orijinal metni değiştirip değiştirmediğini test eder.
Gerçek PDF raporları kullanarak test eder.
"""
import pytest
import json
from pathlib import Path
from typing import Dict, List
import sys
import os

# Proje kök dizinini path'e ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from llm.tools.gemini_segment import segment_text
from llm.tools.pdf_extractor import extract_text


class TestFaithfulExtraction:
    """Faithful extraction testleri - metin değişikliği kontrolü - Gerçek raporlar"""

    @pytest.fixture
    def sample_report_1(self) -> str:
        """Gerçek staj raporu 1: Core4Basis (Türkçe/İngilizce karışık)"""
        pdf_path = project_root / "data" / "sample_reports" / "Core4Basis Intern Report SON.docx - Google Dokümanlar.pdf"
        if not pdf_path.exists():
            pytest.skip(f"PDF dosyası bulunamadı: {pdf_path}")
        return extract_text(pdf_path)

    @pytest.fixture
    def sample_report_2(self) -> str:
        """Gerçek staj raporu 2: Doğuş Teknoloji (Türkçe/İngilizce karışık)"""
        pdf_path = project_root / "data" / "sample_reports" / "Doğuş Teknoloji Intern Report LAST.docx .pdf"
        if not pdf_path.exists():
            pytest.skip(f"PDF dosyası bulunamadı: {pdf_path}")
        return extract_text(pdf_path)

    @pytest.fixture
    def sample_report_3(self) -> str:
        """Örnek staj raporu 3: Basit test senaryosu (hızlı test için)"""
        return """Executive Summary

This report summarizes my internship experience.

1. Company and Sector
a) Overview
The company is a technology firm.

b) Organization
It has multiple departments.

2. Summer Practice Description
I worked on various projects.

3. Conclusions
The internship was valuable."""

    def test_json_structure_valid(self, sample_report_1: str):
        """JSON çıktısının geçerli yapıda olduğunu test et"""
        json_output = segment_text(sample_report_1)
        assert json_output, "JSON çıktısı boş olmamalı"
        
        # JSON parse edilebilir olmalı
        try:
            data = json.loads(json_output)
            assert "segmentation" in data, "JSON'da 'segmentation' anahtarı olmalı"
            assert "sections" in data["segmentation"], "JSON'da 'sections' anahtarı olmalı"
        except json.JSONDecodeError as e:
            pytest.fail(f"JSON parse hatası: {e}")

    def test_no_content_modification(self, sample_report_1: str):
        """İçeriğin değiştirilmediğini test et - karakter karşılaştırması"""
        json_output = segment_text(sample_report_1)
        data = json.loads(json_output)
        
        # Tüm section content'lerini birleştir
        extracted_text = ""
        sections = data.get("segmentation", {}).get("sections", [])
        
        for section in sections:
            content = section.get("content", "")
            if content:
                extracted_text += content + " "
        
        extracted_text = extracted_text.strip()
        
        # Orijinal metindeki tüm kelimelerin çıkarılan metinde de olması gerekir
        original_words = set(sample_report_1.lower().split())
        extracted_words = set(extracted_text.lower().split())
        
        # Önemli kelimelerin çoğu korunmalı (en az %80)
        common_words = original_words.intersection(extracted_words)
        coverage = len(common_words) / len(original_words) if original_words else 0
        
        assert coverage >= 0.8, f"Kelime korunma oranı çok düşük: {coverage:.2%}"

    def test_index_accuracy(self, sample_report_1: str):
        """Karakter indekslerinin doğruluğunu test et"""
        json_output = segment_text(sample_report_1)
        data = json.loads(json_output)
        
        sections = data.get("segmentation", {}).get("sections", [])
        assert len(sections) > 0, "En az bir bölüm bulunmalı"
        
        for section in sections:
            start_idx = section.get("start_idx")
            end_idx = section.get("end_idx")
            content = section.get("content", "")
            
            if start_idx is not None and end_idx is not None:
                # İndeks aralığı pozitif olmalı
                assert start_idx >= 0, "start_idx negatif olamaz"
                assert end_idx > start_idx, "end_idx > start_idx olmalı"
                
                # İçerik uzunluğu indeks aralığıyla uyumlu olmalı
                extracted_length = end_idx - start_idx
                # Tolerans: whitespace farkları olabilir
                assert abs(extracted_length - len(content)) <= 50, \
                    f"İndeks aralığı ile içerik uzunluğu uyumsuz: {extracted_length} vs {len(content)} (section: {section.get('section_id')})"

    def test_no_overlapping_sections(self, sample_report_1: str):
        """Bölümlerin örtüşmediğini test et"""
        json_output = segment_text(sample_report_1)
        data = json.loads(json_output)
        
        sections = data.get("segmentation", {}).get("sections", [])
        ranges = []
        
        for section in sections:
            start_idx = section.get("start_idx")
            end_idx = section.get("end_idx")
            if start_idx is not None and end_idx is not None:
                ranges.append((start_idx, end_idx, section.get("section_id", "unknown")))
        
        # Aralıkları sırala
        ranges.sort(key=lambda x: x[0])
        
        # Örtüşme kontrolü
        for i in range(len(ranges) - 1):
            current_end = ranges[i][1]
            next_start = ranges[i + 1][0]
            
            # Bitiş ile başlangıç arasında en fazla küçük bir boşluk olabilir (whitespace)
            overlap = current_end - next_start
            assert overlap <= 10, \
                f"Bölümler örtüşüyor: {ranges[i][2]} ile {ranges[i+1][2]} arasında {overlap} karakter örtüşme"

    def test_section_hierarchy(self, sample_report_2: str):
        """Hiyerarşik yapının doğru olduğunu test et (alt başlıklar için)"""
        json_output = segment_text(sample_report_2)
        data = json.loads(json_output)
        
        sections = data.get("segmentation", {}).get("sections", [])
        assert len(sections) > 0
        
        # Level değerleri mantıklı olmalı
        for section in sections:
            level = section.get("level")
            parent_id = section.get("parent_id")
            
            if level is not None:
                assert 1 <= level <= 5, f"Level değeri geçersiz: {level}"
                
                # Level > 1 ise parent_id olmalı
                if level > 1:
                    assert parent_id is not None and parent_id != "null", \
                        f"Level {level} bölümünün parent_id'si olmalı: {section.get('section_id')}"

    def test_required_fields_present(self, sample_report_1: str):
        """Gerekli alanların mevcut olduğunu test et"""
        json_output = segment_text(sample_report_1)
        data = json.loads(json_output)
        
        sections = data.get("segmentation", {}).get("sections", [])
        required_fields = ["section_id", "section_name", "content", "start_idx", "end_idx", "level"]
        
        for section in sections:
            for field in required_fields:
                assert field in section, \
                    f"Gerekli alan eksik: {field} (section: {section.get('section_id', 'unknown')})"
                assert section[field] is not None, \
                    f"Gerekli alan null olamaz: {field} (section: {section.get('section_id', 'unknown')})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

