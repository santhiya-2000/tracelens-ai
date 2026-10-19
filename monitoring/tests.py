from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import LLMRequest, Evaluation
from .services.evaluation_service import evaluate_response
from unittest.mock import patch


class EvaluationServiceTests(TestCase):

    def test_correct_response(self):
        result = evaluate_response(
            "What is Django?",
            "Django is a Python web framework.",
            "Django is a Python web framework."
        )

        self.assertTrue(result["passed"])

    def test_incorrect_response(self):
        result = evaluate_response(
            "What is Django?",
            "Django is a database.",
            "Django is a Python web framework."
        )

        self.assertFalse(result["passed"])


class LLMRequestAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_superuser(
            username="testadmin",
            email="test@example.com",
            password="test-password-123"
        )

        self.client.force_authenticate(user=self.user)

        self.llm_request = LLMRequest.objects.create(
            prompt="What is RAG?",
            response="Retrieval-Augmented Generation",
            model_name="mock-llm",
            latency_ms=120,
            input_tokens=4,
            output_tokens=3
        )

    def test_request_saved(self):
        self.assertEqual(
            LLMRequest.objects.count(),
            1
        )

    def test_get_requests(self):
        response = self.client.get("/api/requests/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            1
        )

    def test_request_details(self):
        response = self.client.get(
            f"/api/requests/{self.llm_request.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["prompt"],
            "What is RAG?"
        )

    
    def test_generate_and_evaluate(self):
        response = self.client.post(
            "/api/generate/",
            {
                "prompt": "What is Django?",
                "expected_response": "Django is a Python web framework.",
                "model_name": "mock-llm"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        generated = LLMRequest.objects.get(
            prompt="What is Django?"
        )

        self.assertEqual(
            generated.response,
            "Django is a Python web framework."
        )

        self.assertTrue(generated.evaluation.passed)

        self.assertEqual(generated.traces.count(), 2)


    @patch("monitoring.views.generate_mock_response")
    def test_inference_failure(self, mock_generate):
        mock_generate.side_effect = RuntimeError(
            "Simulated model provider outage"
        )

        response = self.client.post(
            "/api/generate/",
            {
                "prompt": "What is Django?",
                "expected_response": "Django is a Python web framework."
            },
            format="json"
        )

        self.assertEqual(response.status_code, 502)

        failed_request = LLMRequest.objects.get(
            prompt="What is Django?"
        )

        self.assertEqual(failed_request.status, "failed")
        self.assertEqual(failed_request.traces.count(), 1)

        self.assertEqual(
            failed_request.traces.first().stage,
            "inference_error"
        )
