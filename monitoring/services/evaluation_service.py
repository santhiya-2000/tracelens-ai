import re


def tokenize(text):
    return set(
        re.findall(r"\b\w+\b", text.lower())
    )


def evaluate_response(
    prompt,
    response,
    expected_response="",
):
    if not expected_response.strip():
        return {
            "exact_match": False,
            "relevance_score": 0.0,
            "correctness_score": 0.0,
            "passed": False,
            "explanation": "No reference answer supplied; not evaluated.",
            "evaluated": False,
        }

    actual = response.strip().lower()
    expected = expected_response.strip().lower()

    exact_match = actual == expected

    expected_tokens = tokenize(expected)
    actual_tokens = tokenize(actual)

    overlap = len(expected_tokens & actual_tokens)

    relevance = (
        overlap / len(expected_tokens)
        if expected_tokens else 0.0
    )

    passed = relevance >= 0.70

    return {
        "exact_match": exact_match,
        "relevance_score": round(relevance, 3),
        "correctness_score": round(relevance, 3),
        "passed": passed,
        "explanation": (
            "Reference-token coverage passed."
            if passed else
            "Reference-token coverage below threshold."
        ),
        "evaluated": True,
    }
