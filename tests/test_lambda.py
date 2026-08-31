import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Set the environment variables required when lambda_function.py is imported
os.environ["SENDER_EMAIL"] = "musej1998@outlook.com"
os.environ["API_KEY_PARAMETER"] = "/serverless-notification/API_KEY"

from src.lambda_function import lambda_handler


VALID_API_KEY = "MyNotificationKey2026!"


@pytest.fixture
def valid_event():
    return {
        "headers": {
            "x-api-key": VALID_API_KEY
        },
        "body": json.dumps({
            "recipient": "test@example.com",
            "subject": "Test notification",
            "message": "This is a test email."
        })
    }


@patch("src.lambda_function.ssm")
@patch("src.lambda_function.ses")
def test_valid_request(mock_ses, mock_ssm, valid_event):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {
            "Value": VALID_API_KEY
        }
    }

    mock_ses.send_email.return_value = {
        "MessageId": "test-message-id"
    }

    response = lambda_handler(valid_event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["status"] == "success"
    assert body["message"] == "Email sent successfully"
    assert body["message_id"] == "test-message-id"

    mock_ssm.get_parameter.assert_called_once()
    mock_ses.send_email.assert_called_once()


@patch("src.lambda_function.ssm")
def test_invalid_api_key(mock_ssm, valid_event):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {
            "Value": VALID_API_KEY
        }
    }

    valid_event["headers"]["x-api-key"] = "WrongKey"

    response = lambda_handler(valid_event, None)

    assert response["statusCode"] == 401

    body = json.loads(response["body"])

    assert body["status"] == "error"
    assert body["message"] == "Invalid or missing API key"


@patch("src.lambda_function.ssm")
def test_missing_api_key(mock_ssm, valid_event):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {
            "Value": VALID_API_KEY
        }
    }

    valid_event["headers"] = {}

    response = lambda_handler(valid_event, None)

    assert response["statusCode"] == 401

    body = json.loads(response["body"])

    assert body["status"] == "error"
    assert body["message"] == "Invalid or missing API key"


@pytest.mark.parametrize(
    "field",
    ["recipient", "subject", "message"]
)
@patch("src.lambda_function.ssm")
def test_missing_required_field(mock_ssm, valid_event, field):
    mock_ssm.get_parameter.return_value = {
        "Parameter": {
            "Value": VALID_API_KEY
        }
    }

    body = json.loads(valid_event["body"])
    body[field] = ""
    valid_event["body"] = json.dumps(body)

    response = lambda_handler(valid_event, None)

    assert response["statusCode"] == 400

    response_body = json.loads(response["body"])

    assert response_body["status"] == "error"
    assert response_body["message"] == (
        "recipient, subject and message are required"
    )