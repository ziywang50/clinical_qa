import json
import os
import re
import anthropic

SYSTEM_PROMPT = """You are a clinical research query parser. Given a user's medical question, extract structured search keywords optimized for searching ClinicalTrials.gov and PubMed.

Return ONLY valid JSON with this exact schema:
{
  "clinicaltrials": {
    "query": "<2-5 word search string for CT>",
    "phase": "<PHASE1|PHASE2|PHASE3|PHASE4 or null>",
    "status": "<RECRUITING|COMPLETED|ACTIVE_NOT_RECRUITING|NOT_YET_RECRUITING|TERMINATED|SUSPENDED|WITHDRAWN or null>",
    "condition": "<primary condition/disease or null>"
  },
  "pubmed": {
    "query": "<PubMed search string with MeSH-style terms, e.g. GLP-1[tiab] AND diabetes[tiab]>",
    "date_range": "<e.g. 2020:2025 or null>"
  }
}
No explanation, no markdown, only JSON."""


def _fallback_keywords(question: str) -> dict:
    return {
        "clinicaltrials": {
            "query": question[:200],
            "phase": None,
            "status": None,
            "condition": None,
        },
        "pubmed": {
            "query": question[:200],
            "date_range": None,
        },
    }


async def extract_keywords(question: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        message = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        raw = message.content[0].text.strip()
        # Strip optional markdown code fences: ```json ... ``` or ``` ... ```
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except json.JSONDecodeError:
        return _fallback_keywords(question)
    except Exception:
        return _fallback_keywords(question)
