"""
AI-Driven Utilities
NO HARDCODING - Everything from AI reasoning + web search
"""

from .ai_context_fetcher import AIContextFetcher, get_ai_context_fetcher
from .ai_prompts import (
    get_company_ai_prompt,
    get_investor_ai_prompt,
    get_ai_system_prompt,
    get_ai_conclusion_prompt
)

__all__ = [
    'AIContextFetcher',
    'get_ai_context_fetcher',
    'get_company_ai_prompt',
    'get_investor_ai_prompt',
    'get_ai_system_prompt',
    'get_ai_conclusion_prompt'
]