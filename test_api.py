import asyncio
import os
import sys
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

TESTS = [
    {
        "label": "GLP-1 Phase 3 trials",
        "payload": {"question": "What are the latest Phase 3 trials for GLP-1 receptor agonists in type 2 diabetes?"},
    },
    {
        "label": "Pembrolizumab NSCLC",
        "payload": {"question": "What does recent research say about pembrolizumab in non-small cell lung cancer?"},
    },
    {
        "label": "Empty question (validation error)",
        "payload": {"question": ""},
    },
    {
        "label": "Missing field (validation error)",
        "payload": {},
    },
]


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Keyword extractor smoke test — calls Claude directly, no server needed
# ---------------------------------------------------------------------------

async def _smoke_keyword_extractor():
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # Load .env from backend/ so ANTHROPIC_API_KEY is available
    from dotenv import load_dotenv
    load_dotenv(os.path.join(backend_dir, ".env"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from qa.keyword_extractor import extract_keywords

    q = "pembrolizumab non-small cell lung cancer Phase 3"
    return await extract_keywords(q)


def run_keyword_smoke_test():
    print_section("Keyword extractor smoke test (direct Claude call)")
    try:
        result = asyncio.run(_smoke_keyword_extractor())
        ct = result.get("clinicaltrials", {})
        # Fallback returns the exact full input verbatim and all optional fields null
        is_fallback = (
            ct.get("query") == "pembrolizumab non-small cell lung cancer Phase 3"
            and ct.get("phase") is None
            and ct.get("condition") is None
        )
        status = "FALLBACK (Claude call failed)" if is_fallback else "OK — Claude returned structured keywords"
        print(f"  Status  : {status}")
        print(f"  Result  :\n{json.dumps(result, indent=4)}")
    except Exception as e:
        print(f"  ERROR: {e}")


# ---------------------------------------------------------------------------
# HTTP integration tests against the running server
# ---------------------------------------------------------------------------

def run_tests():
    print_section("Health check")
    try:
        r = httpx.get(f"{BASE_URL}/api/health/", timeout=5)
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {r.json()}")
    except Exception as e:
        print(f"  ERROR  : {e}")
        return

    for test in TESTS:
        print_section(test["label"])
        try:
            r = httpx.post(
                f"{BASE_URL}/api/qa/",
                json=test["payload"],
                timeout=60,  # LLM + two external APIs can take a while
            )
            print(f"  Status     : {r.status_code}")

            if r.status_code == 200:
                body = r.json()
                print(f"  Latency    : {body['latency_ms']} ms")
                print(f"  Sources    : {len(body['sources'])}")
                print(f"  Keywords   :\n{json.dumps(body['keywords_used'], indent=4)}")
                print(f"\n  --- Answer (first 500 chars) ---")
                print(f"  {body['answer'][:500]}")
                if len(body['answer']) > 500:
                    print(f"  ... [{len(body['answer'])} chars total]")
                print(f"\n  --- Sources ---")
                for i, src in enumerate(body['sources'], 1):
                    print(f"  [{i}] ({src['source_type']}) {src['source_id']} — {src['title'][:70]}")
            else:
                try:
                    body = r.json()
                    print(f"  Body       :\n{json.dumps(body, indent=4)}")
                except Exception:
                    print(f"  Raw body   : {r.text[:500]}")

        except httpx.TimeoutException:
            print("  ERROR: Request timed out (60s)")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    run_keyword_smoke_test()
    run_tests()
