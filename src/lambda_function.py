import json
import boto3
import os

ses = boto3.client("ses", region_name="eu-west-2")
ssm = boto3.client("ssm", region_name="eu-west-2")

SENDER_EMAIL = os.environ["SENDER_EMAIL"]
API_KEY_PARAMETER = os.environ["API_KEY_PARAMETER"]


def lambda_handler(event, context):
    try:
        headers = event.get("headers") or {}

        request_api_key = (
            headers.get("x-api-key")
            or headers.get("X-API-Key")
        )

        # Retrieve the API key securely from AWS Systems Manager
        parameter = ssm.get_parameter(
            Name=API_KEY_PARAMETER,
            WithDecryption=True
        )

        api_key = parameter["Parameter"]["Value"]

        # Validate the API key
        if request_api_key != api_key:
            return {
                "statusCode": 401,
                "body": json.dumps({
                    "status": "error",
                    "message": "Invalid or missing API key"
                })
            }

        # Parse request body
        body = json.loads(event.get("body", "{}"))

        recipient = body.get("recipient")
        subject = body.get("subject")
        message = body.get("message")

        # Validate required fields
        if not recipient or not subject or not message:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "recipient, subject and message are required"
                })
            }

        # Send email using Amazon SES
        response = ses.send_email(
            Source=SENDER_EMAIL,
            Destination={
                "ToAddresses": [recipient]
            },
            Message={
                "Subject": {
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Data": message
                    }
                }
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": "Email sent successfully",
                "message_id": response["MessageId"]
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }

