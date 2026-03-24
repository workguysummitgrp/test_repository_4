"""Tests for auth endpoints — US-001, US-002, US-003."""

import pytest
from unittest.mock import patch

from backend.app.core.security import create_access_token, decode_access_token, hash_otp, verify_otp, Role


class TestOTPSecurity:
    def test_hash_and_verify_otp(self):
        otp = "123456"
        hashed = hash_otp(otp)
        assert verify_otp(otp, hashed) is True
        assert verify_otp("654321", hashed) is False

    def test_otp_hash_is_not_plaintext(self):
        otp = "123456"
        hashed = hash_otp(otp)
        assert hashed != otp
        assert len(hashed) > 20


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(user_id=1, role="customer")
        payload = decode_access_token(token)
        assert payload["sub"] == "1"
        assert payload["role"] == "customer"

    def test_invalid_token_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_contains_expiry(self):
        token = create_access_token(user_id=42, role="admin")
        payload = decode_access_token(token)
        assert "exp" in payload


class TestRBAC:
    def test_role_enum_values(self):
        assert Role.CUSTOMER.value == "customer"
        assert Role.REVIEWER.value == "reviewer"
        assert Role.APPROVER.value == "approver"
        assert Role.ADMIN.value == "admin"
        assert Role.COMPLIANCE.value == "compliance"

    @pytest.mark.asyncio
    async def test_require_roles_blocks_unauthorized(self):
        guard = Role.ADMIN
        mock_user = {"sub": "1", "role": "customer"}
        from backend.app.core.security import require_roles
        from fastapi import HTTPException
        role_checker = require_roles(Role.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(mock_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_roles_allows_authorized(self):
        mock_user = {"sub": "1", "role": "admin"}
        from backend.app.core.security import require_roles
        role_checker = require_roles(Role.ADMIN)
        result = await role_checker(mock_user)
        assert result["role"] == "admin"
