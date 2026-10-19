from django.shortcuts import render

# Create your views here.

import time

from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import LLMRequest, Evaluation, TraceEvent
from .serializers import (
    LLMRequestSerializer,
    GenerateRequestSerializer,
)
from .services.llm_service import generate_mock_response
from .services.evaluation_service import evaluate_response


class LLMRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        LLMRequest.objects
        .select_related("evaluation")
        .prefetch_related("traces")
        .order_by("-created_at")
    )
    serializer_class = LLMRequestSerializer
    permission_classes = [IsAdminUser]


@api_view(["POST"])
def generate(request):
    if not request.user.is_staff:
        return Response(
            {"detail": "Staff access required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = GenerateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    prompt = serializer.validated_data["prompt"]
    expected = serializer.validated_data["expected_response"]

    start = time.perf_counter()

    try:
        result = generate_mock_response(prompt)

        llm_request = LLMRequest.objects.create(
            prompt=prompt,
            response=result.text,
            expected_response=expected,
            model_name=result.model_name,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            status="success",
        )

        TraceEvent.objects.create(
            request=llm_request,
            stage="inference",
            duration_ms=result.latency_ms,
            metadata={"provider": "mock"},
        )

        if expected.strip():
            eval_start = time.perf_counter()

            scores = evaluate_response(
                prompt,
                result.text,
                expected,
            )

            Evaluation.objects.create(
                request=llm_request,
                exact_match=scores["exact_match"],
                relevance_score=scores["relevance_score"],
                correctness_score=scores["correctness_score"],
                passed=scores["passed"],
                explanation=scores["explanation"],
            )

            TraceEvent.objects.create(
                request=llm_request,
                stage="evaluation",
                duration_ms=round(
                    (time.perf_counter() - eval_start) * 1000,
                    3,
                ),
                metadata={
                    "method": "reference_token_coverage",
                    "groundedness_evaluated": False,
                },
            )

        return Response(
            LLMRequestSerializer(llm_request).data,
            status=status.HTTP_201_CREATED,
        )

    except Exception:
        elapsed = (time.perf_counter() - start) * 1000

        llm_request = LLMRequest.objects.create(
            prompt=prompt,
            expected_response=expected,
            model_name="mock-llm",
            latency_ms=round(elapsed, 3),
            status="failed",
            error_message="Inference failed.",
        )

        TraceEvent.objects.create(
            request=llm_request,
            stage="inference_error",
            duration_ms=round(elapsed, 3),
        )

        return Response(
            {"id": llm_request.id, "error": "Inference failed."},
            status=status.HTTP_502_BAD_GATEWAY,
        )


@api_view(["GET"])
def metrics(request):
    if not request.user.is_staff:
        return Response(
            {"detail": "Staff access required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    total = LLMRequest.objects.count()
    successful = LLMRequest.objects.filter(status="success")

    evaluated = Evaluation.objects.all()

    return Response({
        "total_requests": total,
        "successful_requests": successful.count(),
        "failed_requests": LLMRequest.objects.filter(
            status="failed"
        ).count(),
        "average_latency_ms": successful.aggregate(
            value=Avg("latency_ms")
        )["value"] or 0,
        "evaluated_requests": evaluated.count(),
        "average_reference_coverage": evaluated.aggregate(
            value=Avg("relevance_score")
        )["value"] or 0,
        "passed_evaluations": evaluated.filter(
            passed=True
        ).count(),
    })


from django.shortcuts import render
from django.db.models import Avg
from django.contrib.admin.views.decorators import staff_member_required

from .models import LLMRequest, Evaluation


@staff_member_required
def dashboard(request):

    all_requests = LLMRequest.objects.all()

    total_requests = all_requests.count()

    average_latency = all_requests.aggregate(
        avg=Avg("latency_ms")
    )["avg"] or 0

    evaluations = Evaluation.objects.all()

    context = {
        "total_requests": total_requests,
        "average_latency": average_latency,
        "total_evaluations": evaluations.count(),
        "passed_evaluations": evaluations.filter(
            passed=True
        ).count(),
        "requests": all_requests.order_by("-created_at")[:20],
        "successful_requests": all_requests.filter(
                status="success"
            ).count(),
    }

    return render(
        request,
        "monitoring/dashboard.html",
        context
    )


