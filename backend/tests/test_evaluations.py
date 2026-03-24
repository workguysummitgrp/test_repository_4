"""Tests for evaluation service — US-010, US-011."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from backend.app.schemas.evaluation import EvaluationResult
from backend.app.services.evaluation_service import validate_evaluation_output


class TestValidateEvaluationOutput:
    def test_valid_output(self):
        raw = json.dumps({"score": 85, "confidence": "high", "summary": "Good application", "flags": []})
        result = validate_evaluation_output(raw)
        assert result.score == 85
        assert result.confidence == "high"
        assert result.summary == "Good application"
        assert result.flags == []

    def test_valid_output_with_flags(self):
        raw = json.dumps({
            "score": 45,
            "confidence": "low",
            "summary": "Multiple concerns",
            "flags": ["missing_documents", "incomplete_data"],
        })
        result = validate_evaluation_output(raw)
        assert result.score == 45
        assert len(result.flags) == 2

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            validate_evaluation_output("not json")

    def test_missing_required_field_raises(self):
        raw = json.dumps({"score": 85})
        with pytest.raises(Exception):  # Pydantic ValidationError
            validate_evaluation_output(raw)

    def test_score_out_of_range_raises(self):
        raw = json.dumps({"score": 150, "confidence": "high", "summary": "test", "flags": []})
        with pytest.raises(Exception):
            validate_evaluation_output(raw)

    def test_invalid_confidence_raises(self):
        raw = json.dumps({"score": 85, "confidence": "very_high", "summary": "test", "flags": []})
        with pytest.raises(Exception):
            validate_evaluation_output(raw)

    def test_score_boundary_zero(self):
        raw = json.dumps({"score": 0, "confidence": "low", "summary": "Rejected", "flags": []})
        result = validate_evaluation_output(raw)
        assert result.score == 0

    def test_score_boundary_hundred(self):
        raw = json.dumps({"score": 100, "confidence": "high", "summary": "Perfect", "flags": []})
        result = validate_evaluation_output(raw)
        assert result.score == 100
