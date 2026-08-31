variable "aws_region" {
  description = "AWS region used to deploy the platform"
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "AWS Serverless Notification Platform"
}

variable "sender_email" {
  description = "Verified SES sender email address"
  type        = string
}