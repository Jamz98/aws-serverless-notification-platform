terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "eu-west-2"
}
resource "aws_s3_bucket" "notification_platform" {
  bucket_prefix = "notification-platform-"

  tags = {
    Project = "AWS Serverless Notification Platform"
  }
}

resource "aws_s3_bucket_public_access_block" "notification_platform" {
  bucket = aws_s3_bucket.notification_platform.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "notification_platform" {
  bucket = aws_s3_bucket.notification_platform.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "notification_platform" {
  bucket = aws_s3_bucket.notification_platform.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda_function.py"
  output_path = "${path.module}/../build/lambda_function.zip"
}
resource "aws_iam_role" "lambda_role" {
  name = "serverless-notification-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "notification_platform" {
  function_name = "serverless-notification-platform"

  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"
  handler = "lambda_function.lambda_handler"

  role = aws_iam_role.lambda_role.arn
  environment {
    variables = {
      SENDER_EMAIL      = "musej1998@outlook.com"
      API_KEY_PARAMETER = "/serverless-notification/API_KEY"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution
  ]

  tags = {
    Project = "AWS Serverless Notification Platform"
  }
}
resource "aws_apigatewayv2_api" "notification_api" {
  name          = "serverless-notification-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers = ["content-type"]
  }

  tags = {
    Project = "AWS Serverless Notification Platform"
  }
}
resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.notification_api.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.notification_platform.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "notification" {
  api_id = aws_apigatewayv2_api.notification_api.id

  route_key          = "POST /notify"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "NONE"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.notification_api.id

  name        = "$default"
  auto_deploy = true
}
resource "aws_lambda_permission" "api_gateway" {
  statement_id = "AllowAPIGatewayInvoke"

  action = "lambda:InvokeFunction"

  function_name = aws_lambda_function.notification_platform.function_name

  principal = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.notification_api.execution_arn}/*/*"
}
resource "aws_iam_role_policy" "lambda_ssm" {
  name = "lambda-read-api-key"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ssm:GetParameter"
        ]

        Resource = "arn:aws:ssm:eu-west-2:567579393844:parameter/serverless-notification/API_KEY"
      }
    ]
  })
}
resource "aws_iam_role_policy" "lambda_ses" {
  name = "lambda-ses-send-email"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]

        Resource = "*"
      }
    ]
  })
}