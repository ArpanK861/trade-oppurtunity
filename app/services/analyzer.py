"""
AI analysis service supporting Gemini, OpenAI, Groq, and Anthropic.
Takes search results and generates structured Markdown trade reports.
"""
import httpx
from loguru import logger
from app.config import settings
from app.models.schemas import SearchResult
from app.services.search import format_search_results_for_prompt

# ── Prompt Engineering ─────────────────────────────────────────
def _build_analysis_prompt(sector: str, search_data: str) -> str:
    """
    Build the analysis report prompt.
    """
    clean_sector = sector.replace("-", " ").title()

    return f"""You are an expert trade analyst specializing in Indian markets.
Based on the following real-time data for the **{clean_sector}** sector in India, generate a comprehensive trade report.

─── DATA ───
{search_data}
─── END DATA ───

Generate a professional Markdown report with sections: # Trade Report, Executive Summary, Market Sentiment, Key Players, Current Trade Opportunities, Regulatory Landscape, Risk Assessment, Recommendations, and Sources.
"""
# ── Provider Implementations ───────────────────────────────────
async def _run_groq_analysis(prompt: str) -> str:
    """Run analysis using the Groq API (OpenAI compatible)."""
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60.0)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
        return response.json()["choices"][0]["message"]["content"]

# ── Main Service Logic ─────────────────────────────────────────
async def analyze_sector(sector: str, search_results: list[SearchResult]) -> str:
    """Run market analysis using Groq for a given sector & search data."""
    formatted_data = format_search_results_for_prompt(search_results)
    prompt = _build_analysis_prompt(sector, formatted_data)
    logger.info(f"Using AI provider: groq (model: {settings.GROQ_MODEL})")
    try:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        return await _run_groq_analysis(prompt)
    except Exception as e:
        logger.error(f"Analysis failed for Groq: {e}")
        raise RuntimeError(f"AI analysis failed (Groq): {str(e)}")