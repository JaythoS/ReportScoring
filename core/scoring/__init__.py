"""
Scoring Module

Rubrik kriterlerine göre LLM ile puanlama.
"""
from .segment_scoring import (
    find_cover_segment,
    find_executive_summary_segment,
    score_cover_segment,
    score_executive_summary,
    load_cover_prompt,
    load_executive_prompt
)

__all__ = [
    'find_cover_segment',
    'find_executive_summary_segment',
    'score_cover_segment',
    'score_executive_summary',
    'load_cover_prompt',
    'load_executive_prompt'
]

