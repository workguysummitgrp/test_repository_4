"""AI Evaluation service — OpenAI integration, validation, retry. US-010, US-011, US-026."""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.evaluation import Confidence, Evaluation
from backend.app.schemas.evaluation import EvaluationResult

logger = logging.getLogger(__name__)

EVALUATION_PROMPT = """You are a risk assessment AI for customer onboarding applications.
Evaluate the following application data and return a JSON object with:
- score: integer 0-100 (higher = lower risk, more likely to approve)
- confidence: "low", "medium", or "high"
- summary: brief explanation of the assessment
- flags: array of strings noting any concerns

Application data:
{form_data}

Document metadata:
{doc_metadata}

Respond ONLY with valid JSON matching the schema above."""


async def call_openai(prompt: str) -> dict[str, Any]:
    """Call OpenAI API with structured JSON output."""
    import openai

    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": prompt}],
        temperature=settings.OPENAI_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return {
        "content": response.choices[0].message.content,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        },
    }


def validate_evaluation_output(raw_content: str) -> EvaluationResult:
    """Validate and parse LLM JSON output against schema."""
    data = json.loads(raw_content)
    return EvaluationResult(**data)


async def evaluate_application(
    db: AsyncSession,
    application_id: int,
    form_data: dict,
    doc_metadata: list[dict],
) -> Evaluation:
    """Run AI evaluation with retry logic (max 3 attempts)."""
    prompt = EVALUATION_PROMPT.format(
        form_data=json.dumps(form_data, indent=2),
        doc_metadata=json.dumps(doc_metadata, indent=2),
    )
    raw_input = {"prompt": prompt, "model": settings.OPENAI_MODEL, "temperature": settings.OPENAI_TEMPERATURE}

    last_error: Exception | None = None
    for attempt in range(settings.OPENAI_MAX_RETRIES):
        try:
            response = await call_openai(prompt)
            result = validate_evaluation_output(response["content"])

            evaluation = Evaluation(
                application_id=application_id,
                score=result.score,
                confidence=Confidence(result.confidence),
                summary=result.summary,
                flags=result.flags,
                raw_input=raw_input,
                raw_output={"response": response["content"], "model": response["model"]},
                model_version=response["model"],
                temperature=settings.OPENAI_TEMPERATURE,
                retry_count=attempt,
                is_valid=True,
                evaluated_at=datetime.now(timezone.utc),
            )
            db.add(evaluation)
            await db.flush()
            return evaluation

        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            logger.warning("Evaluation attempt %d failed: %s", attempt + 1, exc)
            continue

    # All retries failed — store invalid evaluation for manual review
    evaluation = Evaluation(
        application_id=application_id,
        score=0,
        confidence=Confidence.LOW,
        summary="Evaluation failed after maximum retries",
        flags=["evaluation_failed"],
        raw_input=raw_input,
        raw_output={"error": str(last_error)},
        model_version=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        retry_count=settings.OPENAI_MAX_RETRIES,
        is_valid=False,
        validation_errors={"error": str(last_error)},
        evaluated_at=datetime.now(timezone.utc),
    )
    db.add(evaluation)
    await db.flush()
    return evaluation
