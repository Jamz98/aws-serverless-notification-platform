output "api_endpoint" {
  description = "API Gateway endpoint for the notification API"
  value       = aws_apigatewayv2_api.notification_api.api_endpoint
}

output "notification_endpoint" {
  description = "POST endpoint for sending notifications"
  value       = "${aws_apigatewayv2_api.notification_api.api_endpoint}/notify"
}

output "lambda_function_name" {
  description = "Name of the notification Lambda function"
  value       = aws_lambda_function.notification_platform.function_name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket used by the platform"
  value       = aws_s3_bucket.notification_platform.bucket
}