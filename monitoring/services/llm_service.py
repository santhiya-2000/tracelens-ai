
from dataclasses import dataclass
import time


@dataclass
class LLMResult:
    text: str
    model_name: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


KNOWLEDGE = {
    "machine learning":
        "Machine learning learns patterns from data.",
    "rag":
        "RAG retrieves external information to support generation.",
    "django":
        "Django is a Python web framework.",
    "api":
        "An API lets software applications communicate.",
}


def generate_mock_response(prompt: str) -> LLMResult:
    start = time.perf_counter()

    normalized = prompt.lower()

    answer = (
        "I do not have a verified answer "
        "for that question."
    )

    for keyword, response in KNOWLEDGE.items():
        if keyword in normalized:
            answer = response
            break

    latency = (time.perf_counter() - start) * 1000

    return LLMResult(
        text=answer,
        model_name="mock-llm",
        input_tokens=len(prompt.split()),
        output_tokens=len(answer.split()),
        latency_ms=round(latency, 3),
    )

import time


def generate_response(prompt):
    start = time.perf_counter()

    knowledge = {
        "django": "Django is a Python web framework.",
        "rag": "RAG retrieves external information to support generation.",
        "machine learning": "Machine learning learns patterns from data.",
        "api": "An API allows applications to communicate.",
    }

    prompt_lower = prompt.lower()
    answer = "I do not have an answer for that question."

    for keyword, value in knowledge.items():
        if keyword in prompt_lower:
            answer = value
            break

    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "response": answer,
        "model_name": "mock-llm",
        "latency_ms": round(latency_ms, 3),
        "input_tokens": len(prompt.split()),
        "output_tokens": len(answer.split()),
    }

