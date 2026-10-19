from django.db import models


class LLMRequest(models.Model):
    prompt = models.TextField()
    response = models.TextField(blank=True)
    model_name = models.CharField(max_length=100, default="mock-llm")
    latency_ms = models.FloatField(default=0)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_name} - Request {self.id}"
    expected_response = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="success",
    )
    error_message = models.TextField(blank=True)


class Evaluation(models.Model):
    request = models.OneToOneField(
        LLMRequest,
        on_delete=models.CASCADE,
        related_name="evaluation"
    )
    relevance_score = models.FloatField(default=0)
    correctness_score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    exact_match = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)


class TraceEvent(models.Model):
    request = models.ForeignKey(
        LLMRequest,
        on_delete=models.CASCADE,
        related_name="traces"
    )
    stage = models.CharField(max_length=100)
    duration_ms = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)