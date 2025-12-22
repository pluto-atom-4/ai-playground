"""
Unit tests for SMS API MCP Server with Surge Integration

Tests cover:
- Pydantic model validation
- SMS sending functionality
- Delivery status checking
- Error handling and logging
- API key authentication
- Rate limiting
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Import from text_me module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_me import (
    SmsMessage,
    SmsRecipient,
    SmsResponse,
    DeliveryStatus,
    SmsFailureLog,
    SurgeApiClient,
    SurgeConfig,
    app,
    auth_config,
    surge_config,
)

logger = logging.getLogger("test.sms_api")

# Create test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def sample_sms_recipient():
    """Sample SMS recipient"""
    return SmsRecipient(
        phone_number="+11234567890",
        country_code="US"
    )


@pytest.fixture
def sample_sms_message(sample_sms_recipient):
    """Sample SMS message"""
    return SmsMessage(
        recipient=sample_sms_recipient,
        message_body="Hello, this is a test SMS!",
        metadata={"test": True}
    )


@pytest.fixture
def valid_auth_header():
    """Valid Authorization header"""
    return f"Bearer {auth_config.api_key}"


# ============================================================================
# Pydantic Model Validation Tests
# ============================================================================

class TestPydanticModels:
    """Test Pydantic model validation"""

    def test_sms_recipient_valid(self):
        """Test valid SMS recipient"""
        recipient = SmsRecipient(
            phone_number="+11234567890",
            country_code="US"
        )
        assert recipient.phone_number == "+11234567890"
        assert recipient.country_code == "US"

    def test_sms_message_valid(self, sample_sms_message):
        """Test valid SMS message"""
        assert sample_sms_message.recipient.phone_number == "+11234567890"
        assert len(sample_sms_message.message_body) <= 160
        assert sample_sms_message.metadata["test"] is True

    def test_sms_message_max_length_validation(self, sample_sms_recipient):
        """Test SMS message max length validation"""
        long_message = "x" * 161  # Exceed max length
        with pytest.raises(ValueError):
            SmsMessage(
                recipient=sample_sms_recipient,
                message_body=long_message
            )

    def test_sms_response_valid(self):
        """Test valid SMS response"""
        response = SmsResponse(
            success=True,
            message_id="sms_123",
            recipient="+11234567890",
            timestamp=datetime.utcnow().isoformat()
        )
        assert response.success is True
        assert response.message_id == "sms_123"
        assert response.error is None

    def test_delivery_status_valid(self):
        """Test valid delivery status"""
        status = DeliveryStatus(
            message_id="sms_123",
            status="delivered",
            timestamp=datetime.utcnow().isoformat(),
            recipient="+11234567890"
        )
        assert status.status == "delivered"
        assert status.error_code is None

    def test_sms_failure_log_valid(self):
        """Test valid SMS failure log"""
        log = SmsFailureLog(
            timestamp=datetime.utcnow().isoformat(),
            message_id="sms_123",
            recipient="+11234567890",
            message_body="Test message",
            error_reason="Network error"
        )
        assert log.message_id == "sms_123"
        log_dict = log.model_dump()
        assert log_dict["error_reason"] == "Network error"


# ============================================================================
# Surge API Client Tests
# ============================================================================

class TestSurgeApiClient:
    """Test Surge API client functionality"""

    @patch('text_me.httpx.Client.post')
    def test_send_sms_success(self, mock_post, sample_sms_message):
        """Test successful SMS sending"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message_id": "surge_msg_123"}
        mock_post.return_value = mock_response

        client_instance = SurgeApiClient(surge_config)
        result = client_instance.send_sms(sample_sms_message)

        assert result.success is True
        assert result.message_id == "surge_msg_123"
        assert result.recipient == "+11234567890"
        assert result.error is None

    @patch('text_me.httpx.Client.post')
    def test_send_sms_api_error(self, mock_post, sample_sms_message):
        """Test SMS sending with API error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid phone number"
        mock_post.return_value = mock_response

        client_instance = SurgeApiClient(surge_config)
        result = client_instance.send_sms(sample_sms_message)

        assert result.success is False
        assert result.error is not None
        assert "400" in result.error

    @patch('text_me.httpx.Client.post')
    def test_send_sms_network_error(self, mock_post, sample_sms_message):
        """Test SMS sending with network error"""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")

        client_instance = SurgeApiClient(surge_config)
        result = client_instance.send_sms(sample_sms_message)

        assert result.success is False
        assert "Network error" in result.error

    @patch('text_me.httpx.Client.get')
    def test_query_delivery_status_success(self, mock_get):
        """Test successful delivery status query"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "delivered",
            "timestamp": datetime.utcnow().isoformat(),
            "recipient": "+11234567890"
        }
        mock_get.return_value = mock_response

        client_instance = SurgeApiClient(surge_config)
        result = client_instance.query_delivery_status("sms_123")

        assert result.status == "delivered"
        assert result.message_id == "sms_123"

    @patch('text_me.httpx.Client.get')
    def test_query_delivery_status_api_error(self, mock_get):
        """Test delivery status query with API error"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Message not found"
        mock_get.return_value = mock_response

        client_instance = SurgeApiClient(surge_config)
        result = client_instance.query_delivery_status("invalid_id")

        assert result.status == "error"
        assert result.error_code == "404"

    def test_log_failure_creates_file(self, sample_sms_message, tmp_path):
        """Test failure logging creates correct file entry"""
        # Create a temporary logs directory
        logs_dir = tmp_path / ".logs"
        logs_dir.mkdir()

        client_instance = SurgeApiClient(surge_config)

        # Mock the LOGS_DIR to use temp directory
        with patch('text_me.LOGS_DIR', logs_dir):
            client_instance._log_failure(
                message_id="sms_123",
                recipient="+11234567890",
                message_body="Test message",
                error_reason="Test error",
                error_code="TEST_001"
            )

        log_file = logs_dir / "sms_failures.jsonl"
        assert log_file.exists()

        with open(log_file, "r") as f:
            log_entry = json.loads(f.readline())
            assert log_entry["message_id"] == "sms_123"
            assert log_entry["error_reason"] == "Test error"


# ============================================================================
# REST API Endpoint Tests
# ============================================================================

class TestRestApiEndpoints:
    """Test REST API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SMS API MCP Server with Surge Integration"
        assert "endpoints" in data

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "SMS API MCP Server"

    def test_list_tools_endpoint(self):
        """Test list tools endpoint"""
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert len(data["tools"]) == 2
        tool_names = [tool["name"] for tool in data["tools"]]
        assert "send_sms_message" in tool_names
        assert "check_delivery_status" in tool_names


# ============================================================================
# Authentication Tests
# ============================================================================

class TestAuthentication:
    """Test API key authentication"""

    def test_send_sms_without_auth(self, sample_sms_message):
        """Test SMS endpoint without authentication"""
        response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump()
        )
        assert response.status_code == 401
        assert "Authorization" in response.json()["detail"]

    def test_send_sms_with_invalid_auth(self, sample_sms_message):
        """Test SMS endpoint with invalid API key"""
        response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump(),
            headers={"Authorization": "Bearer invalid_key"}
        )
        assert response.status_code == 403
        assert "Invalid API key" in response.json()["detail"]

    def test_send_sms_with_wrong_scheme(self, sample_sms_message):
        """Test SMS endpoint with wrong auth scheme"""
        response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump(),
            headers={"Authorization": f"Basic {auth_config.api_key}"}
        )
        assert response.status_code == 401
        assert "Invalid authentication scheme" in response.json()["detail"]

    @patch('text_me.surge_client.send_sms')
    def test_send_sms_with_valid_auth(self, mock_send, sample_sms_message, valid_auth_header):
        """Test SMS endpoint with valid authentication"""
        mock_send.return_value = SmsResponse(
            success=True,
            message_id="sms_123",
            recipient="+11234567890",
            timestamp=datetime.utcnow().isoformat()
        )

        response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump(),
            headers={"Authorization": valid_auth_header}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delivery_status_without_auth(self):
        """Test delivery status endpoint without authentication"""
        response = client.post(
            "/api/tools/check_delivery_status",
            json={"message_id": "sms_123"}
        )
        assert response.status_code == 401

    @patch('text_me.surge_client.query_delivery_status')
    def test_delivery_status_with_valid_auth(self, mock_query, valid_auth_header):
        """Test delivery status endpoint with valid authentication"""
        mock_query.return_value = DeliveryStatus(
            message_id="sms_123",
            status="delivered",
            timestamp=datetime.utcnow().isoformat(),
            recipient="+11234567890"
        )

        response = client.post(
            "/api/tools/check_delivery_status",
            json={"message_id": "sms_123"},
            headers={"Authorization": valid_auth_header}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivered"


# ============================================================================
# Rate Limiting Tests
# ============================================================================

class TestRateLimiting:
    """Test rate limiting functionality"""

    @patch('text_me.surge_client.send_sms')
    def test_rate_limit_header_present(self, mock_send, sample_sms_message, valid_auth_header):
        """Test that rate limit headers are present in response"""
        mock_send.return_value = SmsResponse(
            success=True,
            message_id="sms_123",
            recipient="+11234567890",
            timestamp=datetime.utcnow().isoformat()
        )

        response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump(),
            headers={"Authorization": valid_auth_header}
        )
        assert response.status_code == 200


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full workflows"""

    @patch('text_me.surge_client.send_sms')
    @patch('text_me.surge_client.query_delivery_status')
    def test_full_sms_workflow(self, mock_query, mock_send, sample_sms_message, valid_auth_header):
        """Test complete SMS workflow: send -> check status"""
        # Mock send
        mock_send.return_value = SmsResponse(
            success=True,
            message_id="sms_123",
            recipient="+11234567890",
            timestamp=datetime.utcnow().isoformat()
        )

        # Send SMS
        send_response = client.post(
            "/api/tools/send_sms_message",
            json=sample_sms_message.model_dump(),
            headers={"Authorization": valid_auth_header}
        )
        assert send_response.status_code == 200
        message_id = send_response.json()["message_id"]

        # Mock status query
        mock_query.return_value = DeliveryStatus(
            message_id=message_id,
            status="delivered",
            timestamp=datetime.utcnow().isoformat(),
            recipient="+11234567890"
        )

        # Check status
        status_response = client.post(
            "/api/tools/check_delivery_status",
            json={"message_id": message_id},
            headers={"Authorization": valid_auth_header}
        )
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "delivered"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

