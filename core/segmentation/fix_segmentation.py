"""
Segmentation çıktısındaki sorunları düzelt
- Tekrarlanan ID'leri düzelt
- Eksik parent_id'leri ekle
- Overlap'leri düzelt
- Gaps'leri doldur
"""
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List
from datetime import datetime


def fix_duplicate_ids(sections: List[Dict]) -> List[Dict]:
    """Tekrarlanan section_id'leri düzelt - sıralı sayılar ile"""
    section_ids = [s.get('section_id') for s in sections]
    duplicate_ids = [sid for sid, count in Counter(section_ids).items() if count > 1]
    
    if not duplicate_ids:
        return sections
    
    # Her duplicate ID için yeni benzersiz ID oluştur
    id_counter = {}
    fixed_sections = []
    global_id_counter = max([int(s.get('section_id', '').split('_')[-1]) for s in sections if '_' in s.get('section_id', '') and s.get('section_id', '').split('_')[-1].isdigit()], default=0)
    
    for sec in sections:
        section_id = sec.get('section_id')
        if section_id in duplicate_ids:
            if section_id not in id_counter:
                id_counter[section_id] = 1
            else:
                id_counter[section_id] += 1
                global_id_counter += 1
                # Yeni benzersiz ID oluştur
                base_id = section_id.rsplit('_', 1)[0] if '_' in section_id else section_id
                # Section name'e göre daha anlamlı ID oluştur
                section_name = (sec.get('section_name') or '').lower()
                if 'intro' in section_name or 'introduction' in section_name:
                    new_id = f"intro_{global_id_counter}"
                elif 'activity' in section_name:
                    new_id = f"activity_{global_id_counter}"
                elif 'learning' in section_name:
                    new_id = f"learning_{global_id_counter}"
                elif 'connection' in section_name:
                    new_id = f"connection_{global_id_counter}"
                elif 'aspects' in section_name:
                    new_id = f"aspects_{global_id_counter}"
                elif 'outcome' in section_name:
                    new_id = f"outcome_{global_id_counter}"
                elif 'analysis' in section_name:
                    new_id = f"analysis_{global_id_counter}"
                elif 'details' in section_name:
                    new_id = f"details_{global_id_counter}"
                elif 'process' in section_name:
                    new_id = f"process_{global_id_counter}"
                elif 'indicators' in section_name:
                    new_id = f"indicators_{global_id_counter}"
                elif 'issues' in section_name:
                    new_id = f"issues_{global_id_counter}"
                elif 'relevance' in section_name:
                    new_id = f"relevance_{global_id_counter}"
                elif 'project' in section_name:
                    new_id = f"project_{global_id_counter}"
                elif 'description' in section_name:
                    new_id = f"description_{global_id_counter}"
                elif 'definition' in section_name:
                    new_id = f"definition_{global_id_counter}"
                elif 'solution' in section_name:
                    new_id = f"solution_{global_id_counter}"
                elif 'survey' in section_name or 'literature' in section_name:
                    new_id = f"literature_{global_id_counter}"
                elif 'benefits' in section_name:
                    new_id = f"benefits_{global_id_counter}"
                elif 'conclusion' in section_name:
                    new_id = f"conclusion_{global_id_counter}"
                else:
                    new_id = f"{base_id}_{global_id_counter}"
                sec['section_id'] = new_id
        fixed_sections.append(sec)
    
    return fixed_sections


def fix_missing_parents(sections: List[Dict]) -> List[Dict]:
    """Eksik parent_id'leri ekle - akıllı başlık analizi ile"""
    # Tüm section_id'leri bir set'e al
    all_ids = {s.get('section_id') for s in sections}
    
    fixed_sections = []
    for i, sec in enumerate(sections):
        level = sec.get('level', 1)
        parent_id = sec.get('parent_id')
        section_name = (sec.get('section_name') or '').lower()
        
        # Özel durumlar: Başlık analizi ile parent tespiti
        # "b) Organization" → "1. Company and Sector" altında
        if 'organization' in section_name and ('b)' in section_name or 'organization of' in section_name):
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                prev_name = (prev_sec.get('section_name') or '').lower()
                if 'company and sector' in prev_name or prev_sec.get('section_id', '').startswith('company_sector'):
                    sec['parent_id'] = prev_sec.get('section_id')
                    sec['level'] = 2
                    break
        
        # "c) Production/Service" → "1. Company and Sector" altında
        if 'production' in section_name or 'service system' in section_name:
            if 'c)' in section_name or 'production/service' in section_name:
                for j in range(i - 1, -1, -1):
                    prev_sec = sections[j]
                    prev_name = (prev_sec.get('section_name') or '').lower()
                    if 'company and sector' in prev_name or prev_sec.get('section_id', '').startswith('company_sector'):
                        sec['parent_id'] = prev_sec.get('section_id')
                        sec['level'] = 2
                        break
        
        # "- Support and Maintenance" → "c) Production/Service" altında
        if 'support' in section_name and 'maintenance' in section_name:
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                prev_name = (prev_sec.get('section_name') or '').lower()
                if 'production' in prev_name or 'service system' in prev_name:
                    sec['parent_id'] = prev_sec.get('section_id')
                    sec['level'] = 3
                    break
        
        # "d) Professional and Ethical" → "1. Company and Sector" altında
        if 'professional' in section_name and 'ethical' in section_name:
            if 'd)' in section_name:
                for j in range(i - 1, -1, -1):
                    prev_sec = sections[j]
                    prev_name = (prev_sec.get('section_name') or '').lower()
                    if 'company and sector' in prev_name or prev_sec.get('section_id', '').startswith('company_sector'):
                        sec['parent_id'] = prev_sec.get('section_id')
                        sec['level'] = 2
                        break
        
        # "Daily Activities" altındaki günler (Day 1, Day 2, vb.)
        if section_name.startswith('day ') or section_name.startswith('day') or 'day' in section_name[:10].lower():
            # "Daily Activities" ana başlığını bul
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                prev_name = (prev_sec.get('section_name') or '').lower()
                prev_id = prev_sec.get('section_id', '')
                if 'daily activities' in prev_name or prev_id.startswith('daily_activities'):
                    sec['parent_id'] = prev_sec.get('section_id')
                    sec['level'] = 2
                    break
        
        # "Figures" bölümleri - ilgili günün altında olmalı
        if 'figure' in section_name.lower() and ('figure' in section_name.lower() or 'figures' in section_name.lower()):
            # Önceki bölümlere bak, en yakın "Day X" veya "Figures" olmayan bölümü bul
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                prev_name = (prev_sec.get('section_name') or '').lower()
                prev_id = prev_sec.get('section_id', '')
                
                # Eğer önceki bölüm bir "Day" ise, bu Figure'ı ona bağla
                if prev_name.startswith('day ') or prev_id.startswith('day_'):
                    sec['parent_id'] = prev_sec.get('section_id')
                    sec['level'] = 3
                    break
                # Eğer önceki bölüm Daily Activities ise, level 2 yap
                elif 'daily activities' in prev_name or prev_id.startswith('daily_activities'):
                    sec['parent_id'] = prev_sec.get('section_id')
                    sec['level'] = 2
                    break
        
        # Level 2+ bölümler için genel parent_id kontrolü
        if level > 1 and not sec.get('parent_id'):
            # Önceki bölümleri kontrol et, en yakın Level (level-1) bölümü bul
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                if prev_sec.get('level') == level - 1:
                    sec['parent_id'] = prev_sec.get('section_id')
                    break
        
        # Geçersiz parent_id'yi düzelt
        if parent_id and parent_id not in all_ids:
            # En yakın geçerli parent'ı bul
            for j in range(i - 1, -1, -1):
                prev_sec = sections[j]
                if prev_sec.get('level') == level - 1:
                    sec['parent_id'] = prev_sec.get('section_id')
                    break
            else:
                sec['parent_id'] = None
        
        fixed_sections.append(sec)
    
    return fixed_sections


def fix_overlaps_and_gaps(sections: List[Dict], original_text: str) -> List[Dict]:
    """Overlap ve gap'leri düzelt"""
    sorted_sections = sorted(sections, key=lambda x: x.get('start_idx', 0))
    fixed_sections = []
    
    for i, sec in enumerate(sorted_sections):
        start = sec.get('start_idx', 0)
        end = sec.get('end_idx', 0)
        
        # Önceki bölümle overlap var mı kontrol et
        if i > 0:
            prev_sec = fixed_sections[-1]
            prev_end = prev_sec.get('end_idx', 0)
            
            if start < prev_end:
                # Overlap var - önceki bölümün sonunu ayarla
                prev_sec['end_idx'] = start
                # Content'i de güncelle
                if prev_end <= len(original_text):
                    prev_sec['content'] = original_text[prev_sec.get('start_idx', 0):start]
            
            elif start > prev_end:
                # Gap var - bu bölümün başlangıcını önceki bölümün sonuna ayarla
                sec['start_idx'] = prev_end
                # Content'i de güncelle
                if prev_end < len(original_text):
                    gap_content = original_text[prev_end:start]
                    if sec.get('content'):
                        sec['content'] = gap_content + sec.get('content', '')
                    else:
                        sec['content'] = gap_content
        
        # Content'i doğrula ve güncelle
        if start < len(original_text) and end <= len(original_text):
            actual_content = original_text[start:end]
            if not sec.get('content') or len(sec.get('content', '')) < len(actual_content) * 0.5:
                sec['content'] = actual_content
        
        fixed_sections.append(sec)
    
    return fixed_sections


def merge_short_sections(sections: List[Dict], min_length: int = 10) -> List[Dict]:
    """Kısa içerikli bölümleri (sadece sayfa numarası gibi) üst bölüme birleştir"""
    merged_sections = []
    i = 0
    
    while i < len(sections):
        sec = sections[i]
        content = (sec.get('content') or '').strip()
        
        # Eğer sadece sayfa numarası veya çok kısa ise, bir sonraki bölüme birleştir
        if len(content) < min_length and (content.isdigit() or len(content) < 5):
            if i + 1 < len(sections):
                next_sec = sections[i + 1]
                # Önceki bölümün end_idx'ini sonraki bölümün start_idx'ine ayarla
                if merged_sections:
                    merged_sections[-1]['end_idx'] = next_sec.get('start_idx', sec.get('end_idx', 0))
                i += 1
                continue
        
        merged_sections.append(sec)
        i += 1
    
    return merged_sections


def fix_executive_summary_contents(sections: List[Dict], original_text: str) -> List[Dict]:
    """Executive Summary ve Contents içeriğini düzelt - Contents company_sector içine karışmış olabilir"""
    exec_summary_idx = None
    contents_idx = None
    company_sector_idx = None
    
    # Executive Summary, Contents ve Company and Sector bölümlerini bul
    for i, sec in enumerate(sections):
        section_name = (sec.get('section_name') or '').lower()
        if 'executive summary' in section_name:
            exec_summary_idx = i
        elif section_name == 'contents' or section_name == 'içindekiler':
            contents_idx = i
        elif 'company and sector' in section_name:
            company_sector_idx = i
    
    # Contents bölümü varsa ve Executive Summary'den sonra geliyorsa birleştir
    if exec_summary_idx is not None and contents_idx is not None:
        exec_sec = sections[exec_summary_idx]
        contents_sec = sections[contents_idx]
        
        # Contents'in içeriği Executive Summary'nin devamı gibi görünüyorsa birleştir
        contents_content = contents_sec.get('content', '')
        
        # Eğer Contents'in içeriği Executive Summary'nin sonunu tamamlıyorsa
        if len(contents_content) < 500 or ('tools' in contents_content.lower() or 'visual studio' in contents_content.lower() or 'executive summary' in contents_content.lower() or 'contents' in contents_content.lower()):
            # Executive Summary'nin end_idx'ini Contents'in end_idx'ine ayarla
            exec_sec['end_idx'] = contents_sec.get('end_idx', exec_sec.get('end_idx', 0))
            # Contents'i birleştir (exec_sec'in content'ine ekle)
            exec_sec['content'] = exec_sec.get('content', '') + '\n' + contents_content
            # Contents'i listeden çıkar
            sections.pop(contents_idx)
    
    # Company and Sector içinde Contents içeriği varsa temizle
    if company_sector_idx is not None:
        company_sec = sections[company_sector_idx]
        content = company_sec.get('content', '')
        start_idx = company_sec.get('start_idx', 0)
        
        # Contents tablosunu içeriyorsa temizle
        if 'Contents\nExecutive Summary' in content or ('\nContents\n' in content and '1. Company and Sector' in content):
            # Orijinal metinde gerçek "1. Company and Sector" başlığını bul (Contents tablosundan sonraki)
            # Contents tablosu genellikle "4. Daily Activities 20-41\n3\n\n" ile bitiyor
            # Sonra "1. Company and Sector" başlığı geliyor
            real_section_start = original_text.find('1. Company and Sector\n')
            if real_section_start < 0:
                real_section_start = original_text.find('1. Company and Sector')
            
            if real_section_start > 0:
                # Gerçek başlıktan itibaren içeriği al
                # "1. Company and Sector" başlığından sonraki kısmı al
                header_end = real_section_start + len('1. Company and Sector')
                if header_end < len(original_text) and original_text[header_end] == '\n':
                    header_end += 1
                # "a) Overview" veya benzeri alt başlığı bul
                next_section = original_text.find('a) Overview', header_end)
                if next_section < 0:
                    next_section = original_text.find('a. Overview', header_end)
                if next_section > 0:
                    # "1. Company and Sector" başlığından "a) Overview"a kadar içeriği al
                    clean_content = original_text[real_section_start:next_section] + original_text[next_section:company_sec.get('end_idx', len(original_text))]
                    company_sec['content'] = original_text[real_section_start:company_sec.get('end_idx', len(original_text))]
                    company_sec['start_idx'] = real_section_start
                else:
                    # Alt başlık bulunamadı, sadece başlıktan itibaren al
                    company_sec['start_idx'] = real_section_start
                    company_sec['content'] = original_text[real_section_start:company_sec.get('end_idx', len(original_text))]
    
    return sections


def fix_accountability_parent(sections: List[Dict]) -> List[Dict]:
    """accountability_11'i professional_ethical_10'un altına taşı"""
    professional_ethical_id = None
    accountability_idx = None
    
    # Professional and Ethical ve Accountability bölümlerini bul
    for i, sec in enumerate(sections):
        section_name = (sec.get('section_name') or '').lower()
        section_id = sec.get('section_id', '')
        
        if 'professional' in section_name and 'ethical' in section_name and 'd)' in section_name:
            professional_ethical_id = section_id
        elif 'accountability' in section_name and section_id == 'accountability_11':
            accountability_idx = i
    
    # Accountability'yı Professional and Ethical altına taşı
    if professional_ethical_id and accountability_idx is not None:
        sec = sections[accountability_idx]
        sec['parent_id'] = professional_ethical_id
        sec['level'] = 3
    
    return sections


def fix_introduction_sections(sections: List[Dict]) -> List[Dict]:
    """Introduction bölümlerini doğru parent'lara bağla"""
    # Activity 2, Conclusions ve Day 8 bölümlerini bul
    activity_2_id = None
    conclusions_id = None
    day_8_id = None
    
    for sec in sections:
        section_name = (sec.get('section_name') or '').lower()
        section_id = sec.get('section_id', '')
        
        if 'activity 2' in section_name and 'transition' in section_name:
            activity_2_id = section_id
        elif section_name == 'conclusions' and section_id == 'conclusions_2':
            conclusions_id = section_id
        elif section_name == 'day 8' or section_id == 'day_8_1':
            day_8_id = section_id
    
    # Introduction bölümlerini düzelt
    for sec in sections:
        section_name = (sec.get('section_name') or '').lower()
        section_id = sec.get('section_id', '')
        start_idx = sec.get('start_idx', 0)
        
        if 'introduction' in section_name or section_id.startswith('intro_'):
            # intro_1 (13614-14304): Activity 2'nin girişi
            if 13600 <= start_idx <= 14400:
                if activity_2_id:
                    sec['parent_id'] = activity_2_id
                    sec['level'] = 3
            # intro_2 (27161-27577): Conclusions bloğunun parçası
            elif 27000 <= start_idx <= 27600:
                if conclusions_id:
                    sec['parent_id'] = conclusions_id
                    sec['level'] = 2
            # intro_3 (41268-41680): Day 8'in parçası
            elif 41000 <= start_idx <= 41700:
                if day_8_id:
                    sec['parent_id'] = day_8_id
                    sec['level'] = 3
    
    return sections


def fix_daily_activities_levels(sections: List[Dict]) -> List[Dict]:
    """Daily Activities altındaki Figures ve Day'lerin level'larını düzelt"""
    for i, sec in enumerate(sections):
        section_name = (sec.get('section_name') or '').lower()
        section_id = sec.get('section_id', '')
        parent_id = sec.get('parent_id')
        level = sec.get('level', 1)
        
        # Daily Activities altındaki bölümler
        if parent_id:
            parent_sec = next((s for s in sections if s.get('section_id') == parent_id), None)
            if parent_sec:
                parent_name = (parent_sec.get('section_name') or '').lower()
                parent_id_str = parent_sec.get('section_id', '')
                
                # Daily Activities altındaki bölümler
                if 'daily activities' in parent_name or parent_id_str.startswith('daily_activities'):
                    # Day bölümleri level 2 olmalı
                    if section_name.startswith('day ') or section_id.startswith('day'):
                        if level != 2:
                            sec['level'] = 2
                    
                    # Figures bölümleri - parent'ına göre level belirle
                    elif 'figure' in section_name:
                        # Parent'ı bir Day ise level 3
                        if parent_name.startswith('day ') or parent_id_str.startswith('day'):
                            sec['level'] = 3
                        # Parent Daily Activities ise level 2
                        elif 'daily activities' in parent_name or parent_id_str.startswith('daily_activities'):
                            sec['level'] = 2
    
    return sections


def fix_contents_section(sections: List[Dict], original_text: str) -> List[Dict]:
    """Contents bölümünü ekle (Executive Summary ve Company and Sector arasındaki boşluğu doldur)"""
    # Contents bölümü zaten var mı kontrol et
    contents_existing = any(s.get('section_id') == 'contents_1' for s in sections)
    if contents_existing:
        return sections
    
    # Executive Summary ve Company and Sector'ı bul
    exec_summary = next((s for s in sections if 'executive summary' in (s.get('section_name') or '').lower()), None)
    company_sector = next((s for s in sections if 'company and sector' in (s.get('section_name') or '').lower()), None)
    
    if exec_summary and company_sector:
        exec_end = exec_summary.get('end_idx', 0)
        company_start = company_sector.get('start_idx', 0)
        
        # Executive Summary içinde Contents tablosu varsa, onu ayır
        exec_content = exec_summary.get('content', '')
        if 'Contents\nExecutive Summary' in exec_content:
            # Contents tablosunun başlangıcını bul
            contents_start_in_content = exec_content.find('Contents')
            if contents_start_in_content > 0:
                # Executive Summary'nin end_idx'ini Contents'in başlangıcına ayarla
                exec_summary['end_idx'] = exec_summary.get('start_idx', 0) + contents_start_in_content
                exec_summary['content'] = exec_content[:contents_start_in_content].rstrip()
        
        # Aralarında boşluk varsa veya Contents tablosu varsa Contents bölümü ekle
        if company_start > exec_summary.get('end_idx', 0):
            contents_start = exec_summary.get('end_idx', 0)
            contents_sec = {
                "section_id": "contents_1",
                "section_name": "Contents",
                "content": original_text[contents_start:company_start] if contents_start < len(original_text) else "",
                "start_idx": contents_start,
                "end_idx": company_start,
                "level": 1,
                "parent_id": None
            }
            # Executive Summary'den sonra ekle
            exec_idx = sections.index(exec_summary)
            sections.insert(exec_idx + 1, contents_sec)
    
    return sections


def fix_activity_structure(sections: List[Dict]) -> List[Dict]:
    """Activity yapısını düzelt - Learning from Task, Activity 3, alt bölümler"""
    # Learning from Task'ı Activity 2'ye bağla
    learning_1 = next((s for s in sections if s.get('section_id') == 'learning_1'), None)
    activity_2_14 = next((s for s in sections if s.get('section_id') == 'activity_2_14'), None)
    
    if learning_1 and activity_2_14:
        learning_1['parent_id'] = activity_2_14.get('section_id')
        learning_1['level'] = 3
    
    # Activity 3'ü düzelt
    activity_1 = next((s for s in sections if s.get('section_id') == 'activity_1'), None)
    summer_practice = next((s for s in sections if 'summer practice' in (s.get('section_name') or '').lower() and s.get('section_id', '').startswith('summer_practice')), None)
    
    if activity_1 and summer_practice:
        # Activity 3'ü Summer Practice altına al
        activity_1['parent_id'] = summer_practice.get('section_id')
        activity_1['level'] = 2
        # Section name zaten doğru olmalı ama kontrol et
        if 'Activity 3' not in (activity_1.get('section_name') or ''):
            activity_1['section_name'] = "Activity 3: Default \"Dahili Fatura\" Selection for D-Charge in Invoice Acceptance Process"
        
        # Activity 3 altındaki tüm alt bölümleri activity_1'e bağla
        activity_1_id = activity_1.get('section_id')
        for sec in sections:
            sec_id = sec.get('section_id', '')
            # Activity 3 altındaki alt bölümler
            if sec_id in ['tasks_1', 'connection_1', 'aspects_1', 'outcome_1', 'analysis_1']:
                if sec.get('parent_id') == activity_1_id:
                    sec['level'] = 3
        
        # activity_3_15'i Activity 3 altına al
        activity_3_15 = next((s for s in sections if s.get('section_id') == 'activity_3_15'), None)
        if activity_3_15:
            activity_3_15['parent_id'] = activity_1_id
            activity_3_15['level'] = 3
    
    return sections


def fix_conclusions_structure(sections: List[Dict]) -> List[Dict]:
    """Conclusions bölümünü tek çatıya al - Rubric'e göre düzelt (GENEL)"""
    # Impact, Team Work, Self-directed Learning bölümlerini bul (pattern matching)
    impact_sec = None
    team_work_sec = None
    self_learning_sec = None
    
    for sec in sections:
        sec_name = (sec.get('section_name') or '').lower()
        
        # Impact: "A) Impact", "A ) Impact", "a) Impact" gibi formatlar
        if 'impact' in sec_name and (sec.get('level') == 1 or sec.get('level') == 2):
            if 'a )' in sec_name or 'a)' in sec_name or sec_name.strip().startswith('impact'):
                impact_sec = sec
        
        # Team Work: "B) Team Work", "B ) Team Work", "b) Team Work" gibi formatlar
        if ('team work' in sec_name or 'teamwork' in sec_name) and (sec.get('level') == 1 or sec.get('level') == 2):
            if 'b )' in sec_name or 'b)' in sec_name or sec_name.strip().startswith('team'):
                team_work_sec = sec
        
        # Self-directed Learning: "C) Self-directed Learning", "c) Self-directed Learning" gibi formatlar
        if ('self-directed' in sec_name or 'self directed' in sec_name) and (sec.get('level') == 1 or sec.get('level') == 2):
            if 'c)' in sec_name or sec_name.strip().startswith('self'):
                self_learning_sec = sec
    
    # Conclusions ana başlığını bul (pattern matching - herhangi bir "conclusions" veya "3. conclusions" başlığı)
    conclusions_main = None
    for sec in sections:
        sec_name = (sec.get('section_name') or '').lower()
        if ('conclusions' in sec_name or 'conclusion' in sec_name) and sec.get('level') == 1:
            # "3. Conclusions" gibi formatları kontrol et
            if '3.' in sec_name or '3 ' in sec_name or sec_name.strip().startswith('conclusions'):
                conclusions_main = sec
                break
    
    # Eğer yoksa ve alt bölümler varsa oluştur
    if not conclusions_main and (impact_sec or team_work_sec or self_learning_sec):
        # Ana başlığı oluştur
        # En erken başlangıç pozisyonunu bul
        start_idx = min(
            [s.get('start_idx', 0) for s in [impact_sec, team_work_sec, self_learning_sec] if s]
        )
        
        # "3. Conclusions" metnini bul - benzersiz ID oluştur
        max_id = max([int(s.get('section_id', '0').split('_')[-1]) for s in sections if '_' in s.get('section_id', '') and s.get('section_id', '').split('_')[-1].isdigit()], default=0)
        conclusions_main = {
            "section_id": f"conclusions_{max_id + 1}",
            "section_name": "3. Conclusions",
            "content": "3. Conclusions",
            "start_idx": start_idx - 100 if start_idx > 100 else 0,  # Biraz geriye git
            "end_idx": start_idx,
            "level": 1,
            "parent_id": None
        }
        
        # Impact'ten önce ekle
        if impact_sec:
            impact_idx = sections.index(impact_sec)
            sections.insert(impact_idx, conclusions_main)
        else:
            sections.append(conclusions_main)
    
    # Impact, Team Work, Self-directed Learning'i Conclusions altına al
    if conclusions_main:
        main_id = conclusions_main.get('section_id')
        
        if impact_sec:
            impact_sec['parent_id'] = main_id
            impact_sec['level'] = 2
        
        if team_work_sec:
            team_work_sec['parent_id'] = main_id
            team_work_sec['level'] = 2
        
        if self_learning_sec:
            self_learning_sec['parent_id'] = main_id
            self_learning_sec['level'] = 2
        
        # Societal Impact varsa onu da düzelt
        societal_impact = next((s for s in sections if 'societal impact' in (s.get('section_name') or '').lower() and s.get('level') == 1), None)
        if societal_impact:
            societal_impact['parent_id'] = main_id
            societal_impact['level'] = 2
    
    return sections


def fix_conclusions_content(sections: List[Dict], original_text: str) -> List[Dict]:
    """Conclusions içeriğini genişlet - "During my internship..." paragrafını dahil et (GENEL)"""
    # Conclusions ana bölümünü bul
    conclusions_main = None
    for sec in sections:
        sec_name = (sec.get('section_name') or '').lower()
        if ('conclusions' in sec_name or 'conclusion' in sec_name) and sec.get('level') == 1:
            if '3.' in sec_name or sec_name.strip().startswith('conclusions'):
                conclusions_main = sec
                break
    
    if conclusions_main and len(conclusions_main.get('content', '')) < 200:
        # Conclusions başlangıcını bul
        start_idx = conclusions_main.get('start_idx', 0)
        
        # Impact veya ilk alt bölümün başlangıcını bul
        impact_sec = next((s for s in sections if 'impact' in (s.get('section_name') or '').lower() and s.get('parent_id') == conclusions_main.get('section_id')), None)
        if impact_sec:
            impact_start = impact_sec.get('start_idx', 0)
            
            # "During my internship" veya benzeri başlangıç paragrafını bul
            search_text = original_text[start_idx:impact_start]
            
            # "During my internship" veya "During my" ile başlayan paragrafı bul
            during_pos = search_text.find("During my internship")
            if during_pos == -1:
                during_pos = search_text.find("During my")
            if during_pos == -1:
                during_pos = search_text.find("I had")
            if during_pos == -1:
                during_pos = search_text.find("My internship")
            
            if during_pos > 0:
                # Paragrafın sonunu bul (bir sonraki başlığa kadar)
                paragraph_end = search_text.find("\n\n", during_pos)
                if paragraph_end == -1:
                    paragraph_end = len(search_text)
                else:
                    paragraph_end += 2  # \n\n'yi dahil et
                
                # Conclusions içeriğini genişlet
                new_end_idx = start_idx + during_pos + paragraph_end
                conclusions_main['end_idx'] = new_end_idx
                conclusions_main['content'] = original_text[start_idx:new_end_idx]
    
    return sections


def fix_minor_gaps(sections: List[Dict], original_text: str, merge_tolerance: int = 30) -> List[Dict]:
    """Minor gaps (100-150 karakter) düzelt - merge tolerance ile (GENEL)"""
    # Bölümleri sırala
    sections_sorted = sorted([s for s in sections], key=lambda x: x.get('start_idx', 0))
    
    i = 0
    while i < len(sections_sorted) - 1:
        curr_sec = sections_sorted[i]
        next_sec = sections_sorted[i + 1]
        
        curr_end = curr_sec.get('end_idx', 0)
        next_start = next_sec.get('start_idx', 0)
        gap = next_start - curr_end
        
        # 100-150 karakterlik gap varsa ve merge tolerance içindeyse birleştir
        if 100 <= gap <= 150:
            # Küçük gap - önceki bölümü genişlet
            curr_sec['end_idx'] = next_start
            curr_sec['content'] = original_text[curr_sec.get('start_idx', 0):next_start]
            
            # Eğer bir sonraki bölüm çok kısa ise (sadece başlık gibi) birleştir
            next_content_len = len(next_sec.get('content', ''))
            if next_content_len < 200 and next_sec.get('level') == curr_sec.get('level'):
                # Birleştir
                curr_sec['end_idx'] = next_sec.get('end_idx', next_start)
                curr_sec['content'] = original_text[curr_sec.get('start_idx', 0):next_sec.get('end_idx', next_start)]
                # Bir sonraki bölümü sil
                sections_sorted.remove(next_sec)
                sections = [s for s in sections if s.get('section_id') != next_sec.get('section_id')]
                continue
        
        i += 1
    
    return sections


def fix_activity_analysis_levels(sections: List[Dict]) -> List[Dict]:
    """Activity Analysis altındaki bölümleri Level 2 yap (GENEL)"""
    # Activity Analysis / Summer Practice Description'i bul (pattern matching)
    activity_analysis = None
    for sec in sections:
        sec_name = (sec.get('section_name') or '').lower()
        if (('summer practice description' in sec_name or 'activity analysis' in sec_name or '2. summer practice' in sec_name) 
            and sec.get('level') == 1):
            activity_analysis = sec
            break
    
    if activity_analysis:
        activity_id = activity_analysis.get('section_id')
        activity_start = activity_analysis.get('start_idx', 0)
        activity_end = activity_analysis.get('end_idx', 0)
        
        # Activity Analysis'in end_idx'ini düzelt - en son alt bölümün sonuna kadar
        # Activity Analysis içindeki tüm Level 2 bölümlerin en son end_idx'ini bul
        max_sub_end = activity_end
        for sec in sections:
            if sec.get('parent_id') == activity_id:
                max_sub_end = max(max_sub_end, sec.get('end_idx', 0))
        
        # Daily Activities Activity Analysis altında ise, Daily Activities'in sonuna kadar
        daily_activities = next((s for s in sections if 'daily activities' in (s.get('section_name') or '').lower()), None)
        if daily_activities and daily_activities.get('parent_id') == activity_id:
            max_sub_end = max(max_sub_end, daily_activities.get('end_idx', 0))
        
        # Conclusions başlamadan önce bitmeli (overlap önleme)
        conclusions = next((s for s in sections if 'conclusion' in (s.get('section_name') or '').lower() and s.get('level') == 1), None)
        if conclusions:
            conclusions_start = conclusions.get('start_idx', 0)
            max_sub_end = min(max_sub_end, conclusions_start)
        
        activity_analysis['end_idx'] = max_sub_end
        
        # Activity Analysis içindeki Level 1 bölümleri bul ve Level 2 yap
        for sec in sections:
            sec_start = sec.get('start_idx', 0)
            sec_end = sec.get('end_idx', 0)
            sec_name = (sec.get('section_name') or '').lower()
            
            # Activity Analysis içinde mi kontrol et (end_idx kontrolünü gevşet)
            if (sec_start >= activity_start 
                and sec.get('level') == 1 
                and sec.get('section_id') != activity_id):
                
                # "Activity 1", "Activity 2", "Activity 3" gibi bölümler
                if 'activity' in sec_name and ('activity 1' in sec_name or 'activity 2' in sec_name or 'activity 3' in sec_name):
                    sec['parent_id'] = activity_id
                    sec['level'] = 2
                
                # "2.2 Activity Analysis" veya "Activity Analysis" bölümleri
                elif ('activity analysis' in sec_name and ('2.2' in sec_name or sec_name.strip().startswith('activity analysis'))):
                    sec['parent_id'] = activity_id
                    sec['level'] = 2
                
                # "Project" veya "2.3 Project" gibi bölümler
                elif 'project' in sec_name and ('2.3' in sec_name or sec_name.strip().startswith('project')):
                    sec['parent_id'] = activity_id
                    sec['level'] = 2
                
                # "Societal Impact" gibi bölümler (eğer Impact'ten önceyse)
                elif 'societal impact' in sec_name:
                    impact_sec = next((s for s in sections if 'impact' in (s.get('section_name') or '').lower() and 'a )' in (s.get('section_name') or '').lower()), None)
                    if impact_sec and sec_start < impact_sec.get('start_idx', 0):
                        sec['parent_id'] = activity_id
                        sec['level'] = 2
    
    return sections


def fix_duplicate_daily_activities(sections: List[Dict]) -> List[Dict]:
    """Daily Activities tekrarını düzelt ve birleştir - tüm Day X'leri içer (GENEL - TÜM RAPORLAR İÇİN)"""
    import re
    
    # Tüm Daily Activities bölümlerini bul (pattern matching)
    daily_activities_list = [s for s in sections if 'daily activities' in (s.get('section_name') or '').lower()]
    
    if not daily_activities_list:
        return sections
    
    # En uzun Daily Activities bölümünü ana bölüm olarak seç
    daily_activities_list.sort(key=lambda x: x.get('end_idx', 0) - x.get('start_idx', 0), reverse=True)
    keep_sec = daily_activities_list[0]
    keep_id = keep_sec.get('section_id')
    keep_start = keep_sec.get('start_idx', 0)
    keep_end = keep_sec.get('end_idx', 0)
    
    # "Day X" formatını genel regex ile bul (örn. "Day 1", "Day 9", "Day 10", "● Day 1", vb.)
    # "day" kelimesinin başında veya "●" işaretinden sonra gelmesi gerekiyor (yani "Practice" gibi kelimelerdeki "day" değil)
    day_pattern = re.compile(r'(?:^|●|\s)day\s+\d+', re.IGNORECASE)
    
    # Tüm bölümleri start_idx'e göre sırala
    sections_sorted = sorted(sections, key=lambda x: x.get('start_idx', 0))
    
    # Daily Activities bölümünden sonra gelen ve "Day X" formatında olan ardışık bölümleri bul
    daily_activities_idx = next((i for i, s in enumerate(sections_sorted) if s.get('section_id') == keep_id), -1)
    
    if daily_activities_idx == -1:
        return sections
    
    # Daily Activities'den sonra gelen bölümleri kontrol et
    day_sections = []
    for i in range(daily_activities_idx + 1, len(sections_sorted)):
        sec = sections_sorted[i]
        sec_name = (sec.get('section_name') or '').strip()
        content = (sec.get('content') or '').strip()
        
        # "Day X" formatında mı kontrol et
        is_day_section = False
        if day_pattern.search(sec_name) or day_pattern.search(content[:300]):
            is_day_section = True
        
        # Eğer "Day X" formatındaysa, Daily Activities'e dahil edilmeli
        if is_day_section:
            day_sections.append(sec)
        else:
            # Ardışıklık bozuldu - başka bir ana bölüm başladı
            # Ama önce birkaç bölüm daha kontrol et (belki boşluk var)
            if len(day_sections) > 0:
                # Eğer bu bölüm çok kısa ve "Day X" içermiyorsa, ardışıklık devam edebilir
                content_len = len(content)
                if content_len < 100:
                    # Çok kısa, atla ama ardışıklığı kırma
                    continue
            break
    
    # Daily Activities içindeki mevcut "Day X" bölümlerini de bul
    # (içerikte "Day X" geçen ama ayrı bölüm olmayan içerikler)
    for sec in sections:
        if sec.get('section_id') == keep_id:
            continue
        
        sec_start = sec.get('start_idx', 0)
        sec_end = sec.get('end_idx', 0)
        sec_name = (sec.get('section_name') or '').lower()
        content = (sec.get('content') or '').lower()
        
        # Daily Activities'in mevcut end_idx'i içinde mi?
        if sec_start >= keep_start and sec_end <= keep_end:
            if day_pattern.search(sec_name) or day_pattern.search(content[:300]):
                if sec not in day_sections:
                    day_sections.append(sec)
    
    # Tüm Day X bölümlerini birleştir
    if day_sections:
        # En erken başlangıç ve en geç bitiş pozisyonlarını bul
        all_daily = [keep_sec] + day_sections
        min_start = min([s.get('start_idx', 0) for s in all_daily])
        max_end = max([s.get('end_idx', 0) for s in all_daily])
        
        # Ana Daily Activities bölümünü tüm Day X'leri kapsayacak şekilde genişlet
        keep_sec['start_idx'] = min_start
        keep_sec['end_idx'] = max_end
        
        # Diğer Daily Activities bölümlerini sil (eğer varsa)
        # Ayrıca Daily Activities içindeki tüm Day X bölümlerini de sil (çünkü artık Daily Activities içeriği olarak birleştirildi)
        for sec in daily_activities_list[1:]:
            sections = [s for s in sections if s.get('section_id') != sec.get('section_id')]
        
        # Day X bölümlerinden sonra, Daily Activities içinde kalan ve "daily_activities" ID'sine sahip bölümleri de sil
        # (bunlar muhtemelen chunking sırasında oluşturulmuş duplicate'ler)
        for sec in sections[:]:
            sec_name = (sec.get('section_name') or '').lower()
            sec_id = sec.get('section_id', '')
            # Eğer "daily_activities" ID'si var ama keep_id değilse ve Daily Activities içindeyse sil
            if 'daily_activities' in sec_id and sec_id != keep_id:
                sec_start = sec.get('start_idx', 0)
                sec_end = sec.get('end_idx', 0)
                if sec_start >= keep_sec.get('start_idx', 0) and sec_end <= keep_sec.get('end_idx', 0):
                    sections = [s for s in sections if s.get('section_id') != sec_id]
        
        # Day X bölümlerini Daily Activities altına al (Level 3)
        # Ama önce Daily Activities'in içeriğini güncelle (overlap'i önlemek için)
        for sec in day_sections:
            # Parent ID'yi güncelle
            sec['parent_id'] = keep_id
            sec['level'] = 3  # Daily Activities altında Level 3
            
            # Eğer Day X bölümü Daily Activities'in içindeyse (overlap varsa), 
            # Daily Activities'in end_idx'ini düzelt
            sec_start = sec.get('start_idx', 0)
            sec_end = sec.get('end_idx', 0)
            if sec_start >= keep_sec.get('start_idx', 0) and sec_end > keep_sec.get('end_idx', 0):
                keep_sec['end_idx'] = sec_end
    
    return sections


def fix_indices_precision(sections: List[Dict], original_text: str) -> List[Dict]:
    """Executive Summary ve Professional Ethical end_idx'lerini düzelt"""
    # Executive Summary'yi bul
    exec_summary = next((s for s in sections if 'executive summary' in (s.get('section_name') or '').lower() and s.get('level') == 1), None)
    if exec_summary:
        start = exec_summary.get('start_idx', 0)
        # "Contents" veya "1. Company" başlangıcını bul
        next_sec = None
        for sec in sections:
            sec_start = sec.get('start_idx', 0)
            if sec_start > start:
                if not next_sec or sec_start < next_sec.get('start_idx', 0):
                    next_sec = sec
        
        if next_sec:
            # "Contents" veya "Company" başlığını ara
            next_start = next_sec.get('start_idx', 0)
            # "Contents" veya "1. Company" metnini bul
            search_text = original_text[start:next_start]
            contents_pos = search_text.find("Contents")
            company_pos = search_text.find("1. Company")
            
            if contents_pos > 0:
                exec_summary['end_idx'] = start + contents_pos
            elif company_pos > 0:
                exec_summary['end_idx'] = start + company_pos
            else:
                # Bulamazsa bir sonraki bölümün başlangıcı
                exec_summary['end_idx'] = next_start
            
            # Content'i güncelle
            exec_summary['content'] = original_text[exec_summary['start_idx']:exec_summary['end_idx']]
    
    # Professional and Ethical Responsibilities'ı bul
    professional_ethical = next((s for s in sections if 'professional and ethical' in (s.get('section_name') or '').lower() and s.get('level') == 2), None)
    if professional_ethical:
        start = professional_ethical.get('start_idx', 0)
        # "2. Summer Practice" başlangıcını bul
        next_sec = None
        for sec in sections:
            sec_start = sec.get('start_idx', 0)
            if sec_start > start:
                if not next_sec or sec_start < next_sec.get('start_idx', 0):
                    next_sec = sec
        
        if next_sec:
            next_start = next_sec.get('start_idx', 0)
            # "2. Summer Practice" metnini bul
            search_text = original_text[start:next_start]
            summer_practice_pos = search_text.find("2. Summer Practice")
            
            if summer_practice_pos > 0:
                professional_ethical['end_idx'] = start + summer_practice_pos
                # Content'i güncelle
                professional_ethical['content'] = original_text[professional_ethical['start_idx']:professional_ethical['end_idx']]
    
    return sections


def fix_references_and_daily_activities(sections: List[Dict], original_text: str) -> List[Dict]:
    """References ve Daily Activities bölümlerini düzelt (GENEL)"""
    # References'ı bul (pattern matching)
    references_sec = next((s for s in sections if 'references' in (s.get('section_name') or '').lower() and s.get('level') == 1), None)
    if references_sec:
        # Daily Activities'in başlangıcını bul
        daily_activities = next((s for s in sections if 'daily activities' in (s.get('section_name') or '').lower()), None)
        if daily_activities:
            daily_start = daily_activities.get('start_idx', 0)
            # References'ın end_idx'ini Daily Activities'in başlangıcına ayarla
            references_sec['end_idx'] = daily_start
            # Content'i güncelle
            start = references_sec.get('start_idx', 0)
            if start < len(original_text) and daily_start <= len(original_text):
                references_sec['content'] = original_text[start:daily_start]
    
    # Daily Activities başlığını düzelt (pattern matching)
    daily_activities_sec = next((s for s in sections if 'daily activities' in (s.get('section_name') or '').lower() and s.get('level') == 1), None)
    if daily_activities_sec:
        daily_activities_sec['section_name'] = "4. Daily Activities"
        daily_activities_sec['level'] = 2  # Activity Analysis altında olmalı
        daily_activities_sec['parent_id'] = None  # Önce Activity Analysis'i bul
        
        # Activity Analysis'i bul
        activity_analysis = next((s for s in sections if ('summer practice description' in (s.get('section_name') or '').lower() or 'activity analysis' in (s.get('section_name') or '').lower()) and s.get('level') == 1), None)
        if activity_analysis:
            daily_activities_sec['parent_id'] = activity_analysis.get('section_id')
        
        # Tüm günleri Daily Activities altına sabitle (pattern matching - "Day X" formatı)
        daily_id = daily_activities_sec.get('section_id')
        daily_start = daily_activities_sec.get('start_idx', 0)
        daily_end = daily_activities_sec.get('end_idx', 0)
        
        for sec in sections:
            sec_name = (sec.get('section_name') or '').lower()
            sec_start = sec.get('start_idx', 0)
            # "Day X" formatında ve Daily Activities içinde olan bölümler
            if (('day' in sec_name and sec_name.strip().startswith('day')) or 
                ('● day' in sec_name)) and sec_start >= daily_start and sec_start <= daily_end:
                if sec.get('level') != 2 or sec.get('parent_id') != daily_id:
                    sec['parent_id'] = daily_id
                    sec['level'] = 3  # Daily Activities altında Level 3
        
        # Figür bloklarını düzelt (pattern matching - "Figure X" içeren bölümler)
        for sec in sections:
            sec_name = (sec.get('section_name') or '').lower()
            sec_start = sec.get('start_idx', 0)
            sec_end = sec.get('end_idx', 0)
            
            # Figure içeren bölümler - Daily Activities içindeyse Daily Activities altına
            if 'figure' in sec_name and sec_start >= daily_start and sec_start <= daily_end:
                if sec.get('level') != 2 or sec.get('parent_id') != daily_id:
                    sec['parent_id'] = daily_id
                    sec['level'] = 2
            
            # Figure içeren bölümler - Day X içindeyse Day X altına (Level 3)
            # Day X'leri bul
            for day_sec in sections:
                day_name = (day_sec.get('section_name') or '').lower()
                day_start = day_sec.get('start_idx', 0)
                day_end = day_sec.get('end_idx', 0)
                
                if 'day' in day_name and day_name.strip().startswith('day') and day_sec.get('parent_id') == daily_id:
                    # Bu Day içindeki Figure'ları bul
                    if 'figure' in sec_name and sec_start >= day_start and sec_end <= day_end:
                        sec['parent_id'] = day_sec.get('section_id')
                        sec['level'] = 3
    
    # Checklist/Internship Documents'i bağımsız üst seviye yap (pattern matching)
    for sec in sections:
        sec_name = (sec.get('section_name') or '').lower()
        content_lower = (sec.get('content') or '').lower()
        
        # Checklist veya Internship Documents içeren bölümler
        if (('checklist' in sec_name or 'internship documents' in sec_name) or
            ('checklist' in content_lower or 'internship documents' in content_lower or 'internship application' in content_lower)):
            if sec.get('level') != 1:
                sec['section_name'] = "Internship Documents – Checklist"
                sec['parent_id'] = None
                sec['level'] = 1
    
    return sections


def fix_segmentation(json_file: Path, original_text: str) -> Dict:
    """Tüm sorunları düzelt"""
    data = json.loads(json_file.read_text(encoding='utf-8'))
    sections = data.get('segmentation', {}).get('sections', [])
    
    print("🔧 Segmentation düzeltiliyor...")
    print()
    
    # 1. Tekrarlanan ID'leri düzelt
    print("1️⃣ Tekrarlanan ID'ler düzeltiliyor...")
    sections = fix_duplicate_ids(sections)
    
    # 2. Executive Summary ve Contents içeriğini düzelt
    print("2️⃣ Executive Summary ve Contents içeriği düzeltiliyor...")
    sections = fix_executive_summary_contents(sections, original_text)
    
    # 3. Accountability'yı Professional and Ethical altına taşı
    print("3️⃣ Accountability parent_id düzeltiliyor...")
    sections = fix_accountability_parent(sections)
    
    # 4. Introduction bölümlerini düzelt
    print("4️⃣ Introduction bölümleri düzeltiliyor...")
    sections = fix_introduction_sections(sections)
    
    # 5. Eksik parent_id'leri ekle
    print("5️⃣ Eksik parent_id'ler ekleniyor...")
    sections = fix_missing_parents(sections)
    
    # 6. Daily Activities altındaki level'ları düzelt
    print("6️⃣ Daily Activities level'ları düzeltiliyor...")
    sections = fix_daily_activities_levels(sections)
    
    # 6a. Contents bölümünü ekle
    print("6️⃣a Contents bölümü ekleniyor...")
    sections = fix_contents_section(sections, original_text)
    
    # 6b. Activity yapısını düzelt
    print("6️⃣b Activity yapısı düzeltiliyor...")
    sections = fix_activity_structure(sections)
    
    # 6c. Conclusions yapısını düzelt
    print("6️⃣c Conclusions yapısı düzeltiliyor...")
    sections = fix_conclusions_structure(sections)
    
    # 6d. References ve Daily Activities düzeltmeleri
    print("6️⃣d References ve Daily Activities düzeltiliyor...")
    sections = fix_references_and_daily_activities(sections, original_text)
    
    # 6e. Conclusions ana başlığını tekrar kontrol et (kısa bölümler birleştirildikten sonra)
    print("6️⃣e Conclusions ana başlığı kontrol ediliyor...")
    conclusions_main = next((s for s in sections if s.get('section_id') == 'conclusions_main'), None)
    if not conclusions_main:
        # Eğer yoksa tekrar ekle
        sections = fix_conclusions_structure(sections)
    
    # 7. Kısa bölümleri birleştir
    print("7️⃣ Kısa bölümler (sayfa numaraları) birleştiriliyor...")
    sections = merge_short_sections(sections)
    
    # 8. Overlap ve gap'leri düzelt
    print("8️⃣ Overlap ve gap'ler düzeltiliyor...")
    sections = fix_overlaps_and_gaps(sections, original_text)
    
    # 9. Son kontrol: start_idx/end_idx'leri orijinal metne göre düzelt
    print("9️⃣ start_idx/end_idx'ler doğrulanıyor...")
    for sec in sections:
        start = sec.get('start_idx', 0)
        end = sec.get('end_idx', 0)
        
        # Content'i orijinal metinden al
        if start < len(original_text) and end <= len(original_text):
            sec['content'] = original_text[start:end]
        elif start < len(original_text):
            sec['end_idx'] = len(original_text)
            sec['content'] = original_text[start:]
    
    # 10. Company and Sector'ı tekrar düzelt (overlaps sonrası)
    print("🔟 Company and Sector içeriği tekrar düzeltiliyor...")
    sections = fix_executive_summary_contents(sections, original_text)
    
    # 11. Contents bölümünü tekrar kontrol et (Company and Sector düzeltmesinden sonra)
    print("1️⃣1️⃣ Contents bölümü tekrar kontrol ediliyor...")
    sections = fix_contents_section(sections, original_text)
    
    # 12. Conclusions ana başlığını tekrar kontrol et (son kontroller)
    print("1️⃣2️⃣ Conclusions ana başlığı tekrar kontrol ediliyor...")
    sections = fix_conclusions_structure(sections)
    
    # 13. Activity Analysis altındaki bölümleri düzelt (Level 2 olmalı)
    print("1️⃣3️⃣ Activity Analysis yapısı düzeltiliyor...")
    sections = fix_activity_analysis_levels(sections)
    
    # 14. Daily Activities tekrarını düzelt
    print("1️⃣4️⃣ Daily Activities tekrarı düzeltiliyor...")
    sections = fix_duplicate_daily_activities(sections)
    
    # 15. Executive Summary ve Professional Ethical end_idx'lerini düzelt
    print("1️⃣5️⃣ Executive Summary ve Professional Ethical end_idx düzeltiliyor...")
    sections = fix_indices_precision(sections, original_text)
    
    # 16. Conclusions içeriğini genişlet
    print("1️⃣6️⃣ Conclusions içeriği genişletiliyor...")
    sections = fix_conclusions_content(sections, original_text)
    
    # 17. Minor gaps (100-150 karakter) düzelt
    print("1️⃣7️⃣ Minor gaps düzeltiliyor...")
    sections = fix_minor_gaps(sections, original_text, merge_tolerance=30)
    
    # Metadata güncelle
    if 'source_metadata' not in data:
        data['source_metadata'] = {}
    data['source_metadata']['fixed'] = True
    data['source_metadata']['fix_timestamp'] = datetime.now().isoformat()
    
    # Sections'ı güncelle
    data['segmentation']['sections'] = sections
    
    return data


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from core.extraction import extract_text_from_pdf as extract_text
    
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
        pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # En son Doğuş Teknoloji dosyasını bul
        json_file = sorted(
            Path('outputs/segmentations').glob('Dog*'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[0]
        pdf_file = "data/sample_reports/Doğuş Teknoloji Intern Report LAST.docx .pdf"
    
    print(f"📄 Dosya: {json_file.name}")
    print()
    
    # Orijinal metni oku
    original_text = extract_text(pdf_file)
    
    # Düzelt
    fixed_data = fix_segmentation(json_file, original_text)
    
    # Kaydet
    fixed_file = json_file.with_suffix('.fixed.json')
    fixed_file.write_text(
        json.dumps(fixed_data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    print()
    print(f"✅ Düzeltilmiş dosya kaydedildi: {fixed_file.name}")

