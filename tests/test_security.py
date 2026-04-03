"""
Tests for JWT security module.
"""
from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_guest_id,
    generate_guest_token,
    verify_token,
)


class TestGuestId:
    """Tests for guest ID generation."""

    def test_guest_id_is_uuid(self):
        """Guest ID should be a valid UUID string."""
        guest_id = create_guest_id()
        assert len(guest_id) == 36  # UUID format: 8-4-4-4-12
        assert guest_id.count("-") == 4

    def test_guest_ids_are_unique(self):
        """Each call should generate a unique guest ID."""
        ids = {create_guest_id() for _ in range(100)}
        assert len(ids) == 100


class TestTokenCreation:
    """Tests for JWT token creation."""

    def test_create_token_returns_string(self):
        """Token should be a non-empty string."""
        token = create_access_token({"guest_id": "test-001"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_contains_three_parts(self):
        """JWT should have header.payload.signature structure."""
        token = create_access_token({"guest_id": "test-002"})
        parts = token.split(".")
        assert len(parts) == 3


class TestTokenVerification:
    """Tests for JWT token verification."""

    def test_valid_token_decodes_successfully(self):
        """A valid token should decode with correct claims."""
        token = create_access_token({"guest_id": "test-003"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["guest_id"] == "test-003"

    def test_expired_token_returns_none(self):
        """An expired token should return None."""
        token = create_access_token(
            {"guest_id": "test-expired"},
            expires_delta=timedelta(seconds=-10),
        )
        payload = verify_token(token)
        assert payload is None

    def test_invalid_token_returns_none(self):
        """A garbage token should return None."""
        payload = verify_token("not.a.valid.token")
        assert payload is None

    def test_tampered_token_returns_none(self):
        """A token with modified content should fail verification."""
        token = create_access_token({"guest_id": "test-tamper"})
        # Modify the payload section
        parts = token.split(".")
        parts[1] = parts[1][::-1]  # Reverse the payload
        tampered = ".".join(parts)
        payload = verify_token(tampered)
        assert payload is None

    def test_token_without_guest_id_returns_none(self):
        """A token missing the guest_id claim should return None."""
        token = create_access_token({"user": "not-a-guest"})
        payload = verify_token(token)
        assert payload is None


class TestGenerateGuestToken:
    """Tests for the complete guest token generation flow."""

    def test_returns_three_values(self):
        """Should return (token, guest_id, expires_in) tuple."""
        result = generate_guest_token()
        assert len(result) == 3

    def test_token_is_verifiable(self):
        """Generated token should be decodable."""
        token, guest_id, expires_in = generate_guest_token()
        payload = verify_token(token)
        assert payload is not None
        assert payload["guest_id"] == guest_id

    def test_expires_in_is_positive(self):
        """Expiry time should be positive."""
        _, _, expires_in = generate_guest_token()
        assert expires_in > 0
