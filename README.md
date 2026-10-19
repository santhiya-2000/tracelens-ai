# TraceLens AI

### LLM Observability & Evaluation Platform

TraceLens AI is a Django-based prototype designed to help developers monitor LLM requests, investigate inference failures, and evaluate model responses against reference answers.

## Features

- REST APIs built with Django REST Framework
- Mock LLM inference with execution latency tracking
- Reference-answer evaluation using token overlap
- Separate tracking of inference failures and evaluation failures
- Database persistence using Django ORM and SQLite
- Execution tracing for inference and evaluation stages
- Observability dashboard with request and evaluation metrics
- Automated tests using Django TestCase and DRF APIClient

## Architecture

Client → Django REST API → Mock LLM Service → Evaluation Service → Database → Dashboard

## Technology Stack

Python, Django, Django REST Framework, SQLite, HTML, CSS, Django ORM

## API Endpoints

| Endpoint | Description |
|---|---|
| `POST /api/generate/` | Generate and evaluate an LLM response |
| `GET /api/requests/` | View recorded model interactions |
| `GET /api/metrics/` | Retrieve observability metrics |
| `GET /dashboard/` | View the monitoring dashboard |

## Running Locally

1. Create and activate a Python virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Configure `DJANGO_SECRET_KEY` in a local `.env` file.
4. Run `python manage.py migrate`.
5. Create an admin account using `python manage.py createsuperuser`.
6. Start the application using `python manage.py runserver`.
7. Visit `http://127.0.0.1:8000/dashboard/`.

## Testing

Run:

`python manage.py test monitoring`

## Current Scope

The application currently uses a deterministic mock LLM and a reference-token-overlap evaluator. Token counts are word-based approximations, and evaluation scores should not be interpreted as verified factual correctness.

## Planned Enhancements

- Real LLM provider integration
- LLM-as-a-Judge evaluations
- Request-level trace visualization
- Token usage and cost analysis
- Historical quality and latency trends
