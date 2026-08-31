import os
from src.lambda_function import lambda_handler


API_KEY = os.environ["API_KEY"]


valid_event = {
    "headers": {
        "x-api-key": API_KEY
    },
    "body": '{"recipient":"musej1998@outlook.com","subject":"Local API Key Test","message":"This request passed the API key check!"}'
}


invalid_event = {
    "headers": {
        "x-api-key": "wrong-key"
    },
    "body": '{"recipient":"musej1998@outlook.com","subject":"Should Fail","message":"This should not be sent."}'
}


print("VALID REQUEST:")
print(lambda_handler(valid_event, None))

print("\nINVALID REQUEST:")
print(lambda_handler(invalid_event, None))