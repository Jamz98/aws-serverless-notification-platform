import json


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    recipient = body.get("recipient")
    subject = body.get("subject")
    message = body.get("message")

    if not recipient or not subject or not message:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "status": "error",
                "message": "recipient, subject and message are required"
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "success",
            "recipient": recipient,
            "subject": subject,
            "message": message
        })
    }