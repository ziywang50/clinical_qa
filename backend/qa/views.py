import asyncio
import time

import anthropic
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .answer_generator import generate_answer
from .ct_client import fetch_clinical_trials
from .keyword_extractor import extract_keywords
from .pubmed_client import fetch_pubmed
from .serializers import QARequestSerializer


def _format_source(source: dict) -> dict:
    return {
        "source_type": source.get("source_type", ""),
        "source_id": source.get("source_id", ""),
        "title": source.get("title", ""),
        "summary": source.get("content", ""),
        "url": source.get("url", ""),
    }


class QAView(APIView):
    def post(self, request):
        serializer = QARequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data["question"]
        start = time.time()

        try:
            result = async_to_sync(self._run_pipeline)(question, start)
        except anthropic.APIError:
            return Response(
                {"error": "LLM unavailable, please retry"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(result, status=status.HTTP_200_OK)

    async def _run_pipeline(self, question: str, start: float) -> dict:
        keywords = await extract_keywords(question)

        ct_docs, pubmed_docs = await asyncio.gather(
            fetch_clinical_trials(keywords),
            fetch_pubmed(keywords),
        )

        all_sources = ct_docs + pubmed_docs

        answer = await generate_answer(question, all_sources)

        latency_ms = int((time.time() - start) * 1000)

        return {
            "answer": answer,
            "sources": [_format_source(s) for s in all_sources],
            "keywords_used": keywords,
            "latency_ms": latency_ms,
        }


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})
