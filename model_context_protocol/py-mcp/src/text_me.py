"""
SMS API MCP Server with Surge Integration

FastMCP server that exposes Surge SMS operations (send SMS, query delivery status)
through MCP tools and REST API. Includes API key authentication, comprehensive error
handling, logging, and rate limiting.
"""

import json
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Annotated

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sms.api")

# Create logs directory if it doesn't exist
LOGS_DIR = Path(".logs")
LOGS_DIR.mkdir(exist_ok=True)

# Create an MCP server instance
mcp = FastMCP("SurgeEmailSmsServer", json_response=True)


# ============================================================================
# Environment Configuration & Validation
# ============================================================================

class SurgeConfig:
    """Surge SMS API configuration loaded from environment"""

    def __init__(self):
        self.api_key = os.getenv("SURGE_API_KEY")
        self.account_token = os.getenv("SURGE_ACCOUNT_TOKEN")
        self.sender_id = os.getenv("SURGE_SENDER_ID")
        self.api_base_url = "https://api.surge.com/v1"  # Base Surge API URL

        # Validate on startup
        if not all([self.api_key, self.account_token, self.sender_id]):
            missing = []
            if not self.api_key:
                missing.append("SURGE_API_KEY")
            if not self.account_token:
                missing.append("SURGE_ACCOUNT_TOKEN")
            if not self.sender_id:
                missing.append("SURGE_SENDER_ID")
            raise ValueError(f"Missing required Surge API credentials: {', '.join(missing)}")

        logger.info("Surge SMS API credentials loaded and validated")


class FastAPIConfig:
    """FastAPI server configuration loaded from environment"""

    def __init__(self):
        self.host = os.getenv("FASTAPI_HOST", "127.0.0.1")
        self.port = int(os.getenv("FASTAPI_PORT", "8000"))
        self.log_level = os.getenv("FASTAPI_LOG_LEVEL", "info")


class AuthConfig:
    """Authentication configuration loaded from environment"""

    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("Missing required REST API key: API_KEY")
        logger.info("REST API authentication configured")


class RateLimitConfig:
    """Rate limiting configuration loaded from environment"""

    def __init__(self):
        self.requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


# Initialize configurations
try:
    surge_config = SurgeConfig()
    fastapi_config = FastAPIConfig()
    auth_config = AuthConfig()
    rate_limit_config = RateLimitConfig()
    logger.info(f"Rate limiting: {rate_limit_config.requests} requests per {rate_limit_config.window} seconds")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise


# ============================================================================
# Pydantic Models for Validation
# ============================================================================

class SmsRecipient(BaseModel):
    """Model for SMS recipient"""
    phone_number: Annotated[str, Field(description="Phone number in E.164 format (e.g., +1234567890)")]
    country_code: Annotated[str, Field(description="ISO 3166-1 alpha-2 country code")]


class SmsMessage(BaseModel):
    """Model for SMS message"""
    recipient: SmsRecipient
    message_body: Annotated[str, Field(max_length=160, description="SMS message body (max 160 characters)")]
    metadata: Annotated[dict, Field(default_factory=dict, description="Optional metadata for tracking")]


class SmsResponse(BaseModel):
    """Model for SMS send response"""
    success: bool
    message_id: Annotated[str, Field(description="Unique message ID from Surge API")]
    recipient: str
    timestamp: str
    error: Annotated[str | None, Field(default=None, description="Error message if failed")]


class DeliveryStatus(BaseModel):
    """Model for delivery status"""
    message_id: str
    status: Annotated[str, Field(description="Status: pending, delivered, failed, bounced")]
    timestamp: str
    recipient: str
    error_code: Annotated[str | None, Field(default=None, description="Error code if failed")]


class SmsFailureLog(BaseModel):
    """Model for logging failed SMS attempts"""
    timestamp: str
    message_id: str
    recipient: str
    message_body: str
    error_reason: str
    error_code: Annotated[str | None, Field(default=None)]


# ============================================================================
# Surge SMS API Client
# ============================================================================

class SurgeApiClient:
    """Client for Surge SMS API operations"""

    def __init__(self, config: SurgeConfig):
        self.config = config
        self.client = httpx.Client(timeout=10.0)

    def _log_failure(self, message_id: str, recipient: str, message_body: str,
                     error_reason: str, error_code: str | None = None):
        """Log failed SMS attempt to file for manual review"""
        failure_log = SmsFailureLog(
            timestamp=datetime.utcnow().isoformat(),
            message_id=message_id,
            recipient=recipient,
            message_body=message_body,
            error_reason=error_reason,
            error_code=error_code
        )

        log_file = LOGS_DIR / "sms_failures.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(failure_log.model_dump_json() + "\n")
            logger.info(f"Failure logged for message {message_id}")
        except Exception as e:
            logger.error(f"Failed to write failure log: {e}")

    def send_sms(self, message: SmsMessage) -> SmsResponse:
        """
        Send SMS via Surge API

        Args:
            message: SmsMessage object with recipient and body

        Returns:
            SmsResponse with success status and message ID
        """
        message_id = f"sms_{datetime.utcnow().timestamp()}"

        try:
            # Prepare request to Surge API
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Account-Token": self.config.account_token,
                "Content-Type": "application/json"
            }

            payload = {
                "to": message.recipient.phone_number,
                "from": self.config.sender_id,
                "message": message.message_body,
                "country": message.recipient.country_code,
                "metadata": message.metadata or {}
            }

            logger.info(f"Sending SMS to {message.recipient.phone_number} (ID: {message_id})")

            # Example API endpoint (adjust based on actual Surge API)
            response = self.client.post(
                f"{self.config.api_base_url}/sms/send",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                api_response = response.json()
                surge_message_id = api_response.get("message_id", message_id)
                logger.info(f"SMS sent successfully: {surge_message_id}")
                return SmsResponse(
                    success=True,
                    message_id=surge_message_id,
                    recipient=message.recipient.phone_number,
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                error_msg = f"Surge API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                self._log_failure(
                    message_id,
                    message.recipient.phone_number,
                    message.message_body,
                    error_msg,
                    str(response.status_code)
                )
                return SmsResponse(
                    success=False,
                    message_id=message_id,
                    recipient=message.recipient.phone_number,
                    timestamp=datetime.utcnow().isoformat(),
                    error=error_msg
                )

        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            self._log_failure(
                message_id,
                message.recipient.phone_number,
                message.message_body,
                error_msg
            )
            return SmsResponse(
                success=False,
                message_id=message_id,
                recipient=message.recipient.phone_number,
                timestamp=datetime.utcnow().isoformat(),
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            self._log_failure(
                message_id,
                message.recipient.phone_number,
                message.message_body,
                error_msg
            )
            return SmsResponse(
                success=False,
                message_id=message_id,
                recipient=message.recipient.phone_number,
                timestamp=datetime.utcnow().isoformat(),
                error=error_msg
            )

    def query_delivery_status(self, message_id: str) -> DeliveryStatus:
        """
        Query SMS delivery status from Surge API

        Args:
            message_id: Unique message ID to query

        Returns:
            DeliveryStatus with current delivery status
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Account-Token": self.config.account_token
            }

            logger.info(f"Querying delivery status for message {message_id}")

            # Example API endpoint (adjust based on actual Surge API)
            response = self.client.get(
                f"{self.config.api_base_url}/sms/status/{message_id}",
                headers=headers
            )

            if response.status_code == 200:
                api_response = response.json()
                status = DeliveryStatus(
                    message_id=message_id,
                    status=api_response.get("status", "unknown"),
                    timestamp=api_response.get("timestamp", datetime.utcnow().isoformat()),
                    recipient=api_response.get("recipient", "unknown"),
                    error_code=api_response.get("error_code")
                )
                logger.info(f"Status for {message_id}: {status.status}")
                return status
            else:
                error_msg = f"Surge API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return DeliveryStatus(
                    message_id=message_id,
                    status="error",
                    timestamp=datetime.utcnow().isoformat(),
                    recipient="unknown",
                    error_code=str(response.status_code)
                )

        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            return DeliveryStatus(
                message_id=message_id,
                status="error",
                timestamp=datetime.utcnow().isoformat(),
                recipient="unknown",
                error_code="NETWORK_ERROR"
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return DeliveryStatus(
                message_id=message_id,
                status="error",
                timestamp=datetime.utcnow().isoformat(),
                recipient="unknown",
                error_code="UNKNOWN_ERROR"
            )


# Initialize Surge API client
surge_client = SurgeApiClient(surge_config)


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool(
    name="send_sms_message",
    description="Send an SMS message via Surge SMS API"
)
def send_sms_message(
    message: SmsMessage
) -> dict:
    """
    Send an SMS message using Surge API.

    Args:
        message: SmsMessage with recipient and message body

    Returns:
        Dictionary with success status and message ID
    """
    logger.info("MCP tool: send_sms_message called")
    result = surge_client.send_sms(message)
    logger.info(f"Result: success={result.success}, message_id={result.message_id}")
    return result.model_dump()


@mcp.tool(
    name="check_delivery_status",
    description="Check SMS delivery status from Surge API"
)
def check_delivery_status(
    message_id: Annotated[str, Field(description="Message ID to check status for")]
) -> dict:
    """
    Query the delivery status of an SMS message.

    Args:
        message_id: The unique message ID

    Returns:
        Dictionary with delivery status information
    """
    logger.info(f"MCP tool: check_delivery_status called for {message_id}")
    result = surge_client.query_delivery_status(message_id)
    logger.info(f"Status: {result.status}")
    return result.model_dump()


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="SMS API MCP Server with Surge Integration",
    description="FastMCP server for Surge SMS operations with REST API endpoints",
    version="1.0.0"
)

# Setup rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# ============================================================================
# Authentication Dependency
# ============================================================================

async def verify_api_key(authorization: str = Header(None)) -> str:
    """
    Verify API key from Authorization header.
    Expected format: Bearer {API_KEY}
    """
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        scheme, credentials = authorization.split()
        if scheme.lower() != "bearer":
            logger.warning(f"Invalid authentication scheme: {scheme}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer {token}'",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if credentials != auth_config.api_key:
            logger.warning("Invalid API key provided")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )

        return credentials
    except ValueError:
        logger.warning("Malformed Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    SMS API MCP Server - Root endpoint.

    Available endpoints:
    - GET /health - Health check
    - GET /api/tools - List available tools
    - GET /docs - Interactive API documentation (Swagger UI)
    - POST /api/tools/send_sms_message - Send an SMS
    - POST /api/tools/check_delivery_status - Check delivery status
    """
    logger.info("Root endpoint accessed")
    return {
        "service": "SMS API MCP Server with Surge Integration",
        "version": "1.0.0",
        "documentation": "Visit /docs for interactive API documentation",
        "endpoints": [
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/tools", "method": "GET", "description": "List available tools"},
            {"path": "/api/tools/send_sms_message", "method": "POST", "description": "Send SMS message", "auth": "required"},
            {"path": "/api/tools/check_delivery_status", "method": "POST", "description": "Check delivery status", "auth": "required"},
            {"path": "/docs", "method": "GET", "description": "Interactive API documentation"},
            {"path": "/redoc", "method": "GET", "description": "Alternative API documentation"}
        ]
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    logger.info("Health check performed")
    return {
        "status": "ok",
        "service": "SMS API MCP Server",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/tools", tags=["Tools"])
async def list_tools():
    """
    List all available MCP tools.

    Returns:
        List of available tools with descriptions and endpoints
    """
    logger.info("Tools list requested")
    tools = [
        {
            "name": "send_sms_message",
            "description": "Send an SMS message via Surge SMS API",
            "endpoint": "POST /api/tools/send_sms_message",
            "auth": "required"
        },
        {
            "name": "check_delivery_status",
            "description": "Check SMS delivery status from Surge API",
            "endpoint": "POST /api/tools/check_delivery_status",
            "auth": "required"
        }
    ]
    return {"tools": tools, "count": len(tools)}


@app.post("/api/tools/send_sms_message", tags=["Tools"], summary="Send SMS message")
@limiter.limit(f"{rate_limit_config.requests}/{rate_limit_config.window}s")
async def api_send_sms(
    message: SmsMessage,
    _: str = Depends(verify_api_key)
):
    """
    Send an SMS message via Surge API.

    **Authentication:** Required (Bearer token)

    **Parameters:**
    - message: SmsMessage object with recipient phone number and message body

    **Returns:**
    - success: Boolean indicating if SMS was sent
    - message_id: Unique identifier for the message
    - timestamp: When the request was processed
    - error: Error message if failed
    """
    logger.info(f"API: send_sms_message called for {message.recipient.phone_number}")
    try:
        result = send_sms_message(message)
        return result
    except Exception as e:
        logger.error(f"API error in send_sms_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {str(e)}"
        )


@app.post("/api/tools/check_delivery_status", tags=["Tools"], summary="Check delivery status")
@limiter.limit(f"{rate_limit_config.requests}/{rate_limit_config.window}s")
async def api_check_delivery_status(
    message_id: Annotated[str, Field(description="Message ID to check")],
    _: str = Depends(verify_api_key)
):
    """
    Check the delivery status of an SMS message.

    **Authentication:** Required (Bearer token)

    **Parameters:**
    - message_id: Unique message ID to query

    **Returns:**
    - status: Current delivery status (pending, delivered, failed, bounced, error)
    - message_id: The queried message ID
    - recipient: Recipient phone number
    - error_code: Error code if delivery failed
    """
    logger.info(f"API: check_delivery_status called for {message_id}")
    try:
        result = check_delivery_status(message_id)
        return result
    except Exception as e:
        logger.error(f"API error in check_delivery_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check delivery status: {str(e)}"
        )


# ============================================================================
# Graceful Shutdown Handler
# ============================================================================

def handle_shutdown(signum, frame):
    """Handle graceful shutdown on CTRL+C"""
    logger.info("Shutdown signal received (CTRL+C)")
    logger.info("Closing Surge API client connection")
    surge_client.client.close()
    logger.info("SMS API MCP Server stopped")
    exit(0)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Starting SMS API MCP Server with Surge Integration")
    logger.info("=" * 70)
    logger.info(f"Server: {fastapi_config.host}:{fastapi_config.port}")
    logger.info(f"Log Level: {fastapi_config.log_level}")
    logger.info("Available endpoints:")
    logger.info("  GET  /             - Root endpoint")
    logger.info("  GET  /health       - Health check")
    logger.info("  GET  /api/tools    - List available tools")
    logger.info("  POST /api/tools/send_sms_message (auth required)")
    logger.info("  POST /api/tools/check_delivery_status (auth required)")
    logger.info("  GET  /docs         - Interactive API documentation (Swagger)")
    logger.info("  GET  /redoc        - Alternative API documentation (ReDoc)")
    logger.info(f"Rate Limiting: {rate_limit_config.requests} requests per {rate_limit_config.window}s")
    logger.info("Visit http://" + fastapi_config.host + ":" + str(fastapi_config.port) + "/docs for interactive documentation")
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 70)

    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        uvicorn.run(
            app,
            host=fastapi_config.host,
            port=fastapi_config.port,
            log_level=fastapi_config.log_level
        )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        surge_client.client.close()
        exit(0)

