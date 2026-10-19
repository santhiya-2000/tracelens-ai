
from rest_framework import serializers
from .models import LLMRequest, Evaluation, TraceEvent


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = [
            "exact_match",
            "relevance_score",
            "correctness_score",
            "passed",
            "explanation",
        ]


class TraceEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TraceEvent
        fields = [
            "id",
            "stage",
            "duration_ms",
            "metadata",
            "created_at",
        ]



class LLMRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMRequest
        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class GenerateRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        max_length=4000,
        allow_blank=False
    )
    expected_response = serializers.CharField(
        max_length=4000,
        allow_blank=True,
        required=False,
        default=""
    )
    model_name = serializers.ChoiceField(
        choices=["mock-llm"],
        default="mock-llm"
    )
