import pytest
from pydantic import ValidationError

from backend.app.schemas.user import RegisterRequest, OTPVerifyRequest, UserRoleUpdate
from backend.app.schemas.application import DraftSaveRequest, ApplicationCreateRequest
from backend.app.schemas.evaluation import EvaluationResult
from backend.app.schemas.review import ReviewerDecisionRequest, ApproverDecisionRequest
from backend.app.schemas.admin import ThresholdUpdateRequest


class TestUserSchemas:
    def test_valid_register(self):
        req = RegisterRequest(email="user@example.com", full_name="John Doe")
        assert req.email == "user@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", full_name="John")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="user@example.com", full_name="")

    def test_valid_otp(self):
        req = OTPVerifyRequest(email="user@example.com", otp="123456")
        assert req.otp == "123456"

    def test_short_otp_rejected(self):
        with pytest.raises(ValidationError):
            OTPVerifyRequest(email="user@example.com", otp="123")

    def test_non_numeric_otp_rejected(self):
        with pytest.raises(ValidationError):
            OTPVerifyRequest(email="user@example.com", otp="abcdef")

    def test_valid_role_update(self):
        req = UserRoleUpdate(role="reviewer")
        assert req.role == "reviewer"

    def test_invalid_role_rejected(self):
        with pytest.raises(ValidationError):
            UserRoleUpdate(role="superadmin")


class TestApplicationSchemas:
    def test_valid_draft_save(self):
        req = DraftSaveRequest(form_data={"name": "test"}, current_step=1)
        assert req.current_step == 1

    def test_step_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            DraftSaveRequest(form_data={}, current_step=5)

    def test_step_zero_rejected(self):
        with pytest.raises(ValidationError):
            DraftSaveRequest(form_data={}, current_step=0)


class TestEvaluationSchemas:
    def test_valid_evaluation_result(self):
        result = EvaluationResult(score=85, confidence="high", summary="Good", flags=[])
        assert result.score == 85

    def test_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            EvaluationResult(score=-1, confidence="high", summary="", flags=[])

    def test_score_above_100_rejected(self):
        with pytest.raises(ValidationError):
            EvaluationResult(score=101, confidence="high", summary="", flags=[])


class TestReviewSchemas:
    def test_valid_reviewer_decision(self):
        req = ReviewerDecisionRequest(decision="approved")
        assert req.decision == "approved"

    def test_invalid_decision_rejected(self):
        with pytest.raises(ValidationError):
            ReviewerDecisionRequest(decision="maybe")

    def test_approver_requires_comment(self):
        req = ApproverDecisionRequest(decision="approved", comment="Looks good")
        assert req.comment == "Looks good"

    def test_approver_empty_comment_rejected(self):
        with pytest.raises(ValidationError):
            ApproverDecisionRequest(decision="approved", comment="")


class TestAdminSchemas:
    def test_valid_threshold(self):
        req = ThresholdUpdateRequest(band_name="auto_approve", min_score=91, max_score=100)
        assert req.min_score == 91

    def test_negative_score_rejected(self):
        with pytest.raises(ValidationError):
            ThresholdUpdateRequest(band_name="test", min_score=-1, max_score=100)

    def test_score_above_100_rejected(self):
        with pytest.raises(ValidationError):
            ThresholdUpdateRequest(band_name="test", min_score=0, max_score=101)