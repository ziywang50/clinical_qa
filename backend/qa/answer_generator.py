import os
import anthropic
import asyncio

SYSTEM_PROMPT_TEMPLATE = """You are a clinical research assistant. Answer the user's question using ONLY the provided research context below.

Rules:
1. Every factual claim MUST have an inline citation like [1] or [2][3].
2. If the context does not contain enough information to answer, say so clearly.
3. Do not fabricate trial results, statistics, or outcomes not present in the context.
4. Structure your answer: brief direct answer first, then supporting evidence.
5. Do NOT use generic medical disclaimers like "This does not constitute medical advice."

Context:
{context}
"""
#added limitation section
LIMITATION_PROMPT = """
You are given a clinical question and the sources retrieved to answer it.
Write ONLY a "## Limitations" section. Do not repeat the answer.
Address:
- If PubMed or ClinicalTrials.gov returned 0 results, state this gap.
- If evidences are missing key aspects or conflicting, state this
- Specific weaknesses (small sample, single-country, early-phase, etc.).
- If any sources appear irrelevant.
Be specific. Do not use generic disclaimers. Do not write anything other than the limitations section. If there are no limitations found, return an empty string.
"""


def _build_context(sources: list[dict]) -> str:
    lines = []
    for i, source in enumerate(sources, start=1):
        source_type = source.get("source_type", "unknown").upper()
        title = source.get("title", "No title")
        content = source.get("content", "")
        lines.append(f"[{i}] {source_type}: {title}\n{content}")
    return "\n\n".join(lines)

def _trim_at_last_sentence(text: str) -> str:
    """Trim the text at the last sentence boundary."""
    text = text.strip()
    if text.endswith((".", "!", "?", "]", ")")):
        return text
    last_period = text.rfind(".")
    if last_period > 0:
        return text[: last_period + 1]
    return text

async def generate_answer(question: str, sources: list[dict], max_tokens_answer: int = 2048, max_tokens_limitations: int = 384) -> str:
    if not sources:
        return (
            "No relevant studies found for this query. Try rephrasing with different terms. "
            "This summary is for informational purposes only and does not constitute medical advice."
        )

    context = _build_context(sources)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
    ct_count = sum(1 for s in sources if s.get("source_type") == "clinicaltrials")
    pubmed_count = sum(1 for s in sources if s.get("source_type") == "pubmed")

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        answer_msg, limitation_msg = await asyncio.gather(
            client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens_answer,
                system=system_prompt,
                messages=[{"role": "user", "content": question}],
            ),
            client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens_limitations,
                system=LIMITATION_PROMPT,
                messages=[{"role": "user", "content": f"Question: {question}\n\nClinicalTrials.gov returned {ct_count} results. PubMed returned {pubmed_count} results.\n\nContext:\n{context}"}],
            ),
        )
        answer = _trim_at_last_sentence(answer_msg.content[0].text.strip())
        limitations = _trim_at_last_sentence(limitation_msg.content[0].text.strip())
        return f"{answer}\n\n{limitations}"
    except anthropic.APIError:
        raise
