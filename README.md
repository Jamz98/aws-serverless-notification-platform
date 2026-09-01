\# AWS Serverless Notification Platform



A secure, infrastructure-as-code serverless notification platform built on AWS using \*\*API Gateway, AWS Lambda, Amazon SES, AWS Systems Manager Parameter Store, IAM and Terraform\*\*.



The platform exposes an HTTP API that accepts notification requests, validates an API key stored securely in AWS Systems Manager Parameter Store, and sends emails through Amazon SES.



The project also includes automated unit testing with \*\*pytest\*\* and continuous integration using \*\*GitHub Actions\*\*.



\---



\## Architecture



```text

&#x20;                        ┌─────────────────────┐

&#x20;                        │      API Client     │

&#x20;                        │                     │

&#x20;                        │ POST /notify        │

&#x20;                        │ x-api-key: \*\*\*\*\*\*   │

&#x20;                        └──────────┬──────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌─────────────────────┐

&#x20;                        │    API Gateway      │

&#x20;                        │    HTTP API         │

&#x20;                        └──────────┬──────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌─────────────────────┐

&#x20;                        │    AWS Lambda       │

&#x20;                        │                     │

&#x20;                        │ Request validation  │

&#x20;                        │ API key validation  │

&#x20;                        │ Email processing    │

&#x20;                        └──────┬───────┬──────┘

&#x20;                               │       │

&#x20;                    ┌──────────┘       └─────────────┐

&#x20;                    ▼                                ▼

&#x20;         ┌─────────────────────┐          ┌─────────────────────┐

&#x20;         │ AWS SSM Parameter   │          │    Amazon SES       │

&#x20;         │ Store               │          │                     │

&#x20;         │                     │          │ Email delivery      │

&#x20;         │ Secure API key      │          └─────────────────────┘

&#x20;         └─────────────────────┘



&#x20;                        Infrastructure

&#x20;                               │

&#x20;                               ▼

&#x20;                        ┌─────────────────────┐

&#x20;                        │      Terraform      │

&#x20;                        │                     │

&#x20;                        │ Infrastructure as   │

&#x20;                        │ Code                │

&#x20;                        └─────────────────────┘



&#x20;                        Development / CI

&#x20;                               │

&#x20;                   ┌───────────┴───────────┐

&#x20;                   ▼                       ▼

&#x20;            ┌─────────────┐        ┌───────────────┐

&#x20;            │   Pytest    │        │ GitHub Actions│

&#x20;            │ 6 tests     │───────▶│ Automated CI  │

&#x20;            └─────────────┘        └───────────────┘

```



\---



\## Project Overview



This project demonstrates how to build and deploy a production-style serverless API using AWS and Infrastructure as Code.



The application provides an endpoint for sending email notifications without requiring a traditional always-running server.



The Lambda function:



1\. Receives an HTTP request through API Gateway.

2\. Extracts the API key from the request headers.

3\. Retrieves the expected API key securely from AWS Systems Manager Parameter Store.

4\. Validates the API key.

5\. Validates the required request fields.

6\. Sends the email using Amazon SES.

7\. Returns a structured JSON response.



\---



\## AWS Services Used



| Service                                 | Purpose                                                     |

| --------------------------------------- | ----------------------------------------------------------- |

| \*\*Amazon API Gateway\*\*                  | Provides the public HTTP API endpoint                       |

| \*\*AWS Lambda\*\*                          | Runs the notification application without managing servers  |

| \*\*Amazon SES\*\*                          | Sends email notifications                                   |

| \*\*AWS Systems Manager Parameter Store\*\* | Securely stores the API key                                 |

| \*\*AWS IAM\*\*                             | Controls access between AWS services                        |

| \*\*Amazon S3\*\*                           | Supports the project infrastructure/deployment architecture |

| \*\*Amazon CloudWatch\*\*                   | Provides Lambda logging and monitoring                      |

| \*\*Terraform\*\*                           | Provisions and manages AWS infrastructure                   |



\---



\## Security



Security was considered throughout the design rather than embedding credentials directly in application code.



\### API Key Management



The API key is stored in:



```text

AWS Systems Manager Parameter Store

```



using a secure parameter.



The Lambda function retrieves the value at runtime rather than storing the secret directly in the source code.



The application expects the API key through the request header:



```text

x-api-key: <your-api-key>

```



Invalid or missing API keys return:



```json

{

&#x20; "status": "error",

&#x20; "message": "Invalid or missing API key"

}

```



with HTTP status:



```text

401 Unauthorized

```



\### IAM Least Privilege



Lambda is granted only the permissions required by the application.



For example, the Lambda execution role includes permission to retrieve the specific API key parameter:



```text

ssm:GetParameter

```



rather than granting unrestricted Systems Manager access.



The Lambda execution role also has the permissions required for email delivery through Amazon SES and CloudWatch logging.



\### Secrets and Terraform State



Sensitive configuration is intentionally excluded from Git.



The repository ignores:



```text

terraform.tfvars

\*.tfstate

\*.tfstate.\*

.env

```



Generated files and local development artefacts are also excluded.



\---



\## API



\### Endpoint



```text

POST /notify

```



\### Headers



```text

Content-Type: application/json

x-api-key: <your-api-key>

```



\### Request Body



```json

{

&#x20; "recipient": "recipient@example.com",

&#x20; "subject": "Test notification",

&#x20; "message": "Hello from the AWS Serverless Notification Platform"

}

```



\### Successful Response



```json

{

&#x20; "status": "success",

&#x20; "message": "Email sent successfully",

&#x20; "message\_id": "..."

}

```



\### Invalid API Key



```json

{

&#x20; "status": "error",

&#x20; "message": "Invalid or missing API key"

}

```



HTTP status:



```text

401

```



\### Missing Required Fields



The API validates:



\* `recipient`

\* `subject`

\* `message`



If one or more fields are missing, the API returns HTTP `400`.



\---



\## Infrastructure as Code



The infrastructure is managed using \*\*Terraform\*\*.



Terraform provisions and manages the AWS resources required by the application, including:



\* Lambda

\* API Gateway

\* IAM roles and policies

\* S3

\* Lambda permissions

\* API Gateway integration

\* API Gateway routes

\* API Gateway stage

\* Supporting configuration



This allows the environment to be reproduced consistently rather than relying on manually configured AWS resources.



\### Terraform Workflow



Initialize Terraform:



```bash

terraform -chdir=terraform init

```



Validate the configuration:



```bash

terraform -chdir=terraform validate

```



Review infrastructure changes:



```bash

terraform -chdir=terraform plan

```



Apply infrastructure:



```bash

terraform -chdir=terraform apply

```



Destroy the infrastructure when no longer required:



```bash

terraform -chdir=terraform destroy

```



\---



\## Testing



The project includes automated unit tests using \*\*pytest\*\*.



The test suite covers:



\* Valid API requests

\* Invalid API keys

\* Missing API keys

\* Missing `recipient`

\* Missing `subject`

\* Missing `message`



Run the automated tests:



```bash

python -m pytest tests/ -v

```



Current test result:



```text

6 passed

```



Example:



```text

tests/test\_lambda.py::test\_valid\_request PASSED

tests/test\_lambda.py::test\_invalid\_api\_key PASSED

tests/test\_lambda.py::test\_missing\_api\_key PASSED

tests/test\_lambda.py::test\_missing\_required\_field\[recipient] PASSED

tests/test\_lambda.py::test\_missing\_required\_field\[subject] PASSED

tests/test\_lambda.py::test\_missing\_required\_field\[message] PASSED

```



\---



\## Continuous Integration



GitHub Actions automatically runs the test suite when changes are pushed to the `main` branch or when a pull request targets `main`.



The CI workflow:



1\. Checks out the repository.

2\. Installs Python 3.12.

3\. Installs project dependencies.

4\. Runs the automated pytest suite.



Workflow:



```text

Git Push / Pull Request

&#x20;         │

&#x20;         ▼

&#x20;   GitHub Actions

&#x20;         │

&#x20;         ▼

&#x20;   Install Python

&#x20;         │

&#x20;         ▼

&#x20;Install Dependencies

&#x20;         │

&#x20;         ▼

&#x20;     Run Pytest

&#x20;         │

&#x20;         ▼

&#x20;     6 Tests

&#x20;         │

&#x20;         ▼

&#x20;      PASS ✓

```



This prevents changes from being merged without passing the automated test suite.



\---



\## Local Testing



A separate local integration test is also included:



```text

test\_local.py

```



This allows the Lambda handler to be tested locally with representative requests.



The local testing workflow was used to verify both successful and unsuccessful requests.



Example successful response:



```text

statusCode: 200

Email sent successfully

```



Example unsuccessful response:



```text

statusCode: 401

Invalid or missing API key

```



\---



\## Project Structure



```text

aws-serverless-notification-platform/

│

├── .github/

│   └── workflows/

│       └── tests.yml

│

├── src/

│   └── lambda\_function.py

│

├── tests/

│   └── test\_lambda.py

│

├── terraform/

│   ├── main.tf

│   ├── variables.tf

│   ├── outputs.tf

│   └── .terraform.lock.hcl

│

├── requirements.txt

├── test\_local.py

├── .gitignore

└── README.md

```



Generated files such as Terraform state, provider binaries, Python caches and build artefacts are intentionally excluded from version control.



\---



\## Deployment Outputs



The deployed infrastructure currently provides:



```text

Lambda:

serverless-notification-platform



API:

API Gateway HTTP API



Region:

eu-west-2

```



Terraform exposes the following outputs:



```text

api\_endpoint

notification\_endpoint

lambda\_function\_name

s3\_bucket\_name

```



Sensitive credentials are not exposed through Terraform outputs.



\---



\## Technical Skills Demonstrated



This project demonstrates practical experience with:



\### Cloud



\* AWS Lambda

\* Amazon API Gateway

\* Amazon SES

\* Amazon S3

\* AWS Systems Manager Parameter Store

\* AWS IAM

\* Amazon CloudWatch



\### Infrastructure



\* Terraform

\* Infrastructure as Code

\* Terraform variables

\* Terraform outputs

\* IAM policy configuration

\* AWS resource dependencies



\### Development



\* Python

\* boto3

\* JSON APIs

\* HTTP request validation

\* Error handling

\* Unit testing

\* pytest



\### DevOps



\* Git

\* GitHub

\* GitHub Actions

\* Continuous Integration

\* Automated testing

\* Version-controlled infrastructure



\### Security



\* API authentication

\* Secure parameter storage

\* IAM least privilege

\* Separation of application code and secrets

\* Exclusion of sensitive configuration from Git



\---



\## Challenges and Troubleshooting



Several real-world development issues were identified and resolved during the project.



\### Python Dependency Management



The local environment initially lacked `boto3` and `pytest`. Dependencies were installed and documented so the project could be reproduced in a clean environment.



\### API Authentication



The API initially returned:



```text

401 Invalid or missing API key

```



The request headers and API key configuration were corrected and successfully tested.



\### Secure API Key Storage



The API key was moved away from application source code into AWS Systems Manager Parameter Store.



Lambda was then given permission to retrieve the specific parameter through IAM.



\### Lambda Environment Variables



The Lambda deployment initially failed because the required `API\_KEY\_PARAMETER` environment variable was missing.



The Terraform configuration was updated to provide the required environment configuration.



\### GitHub Actions Test Discovery



The CI workflow initially attempted to collect `test\_local.py`, causing the GitHub runner to fail because local environment variables were not available.



The workflow was corrected to explicitly run:



```bash

python -m pytest tests/ -v

```



The automated CI pipeline subsequently passed all six tests.



\### Terraform Provider Files



Terraform provider binaries were initially included in Git, resulting in GitHub rejecting the repository because the AWS provider binary exceeded GitHub's 100 MB file limit.



The `.terraform` directory and generated files were removed from version control and added to `.gitignore`.



\---



\## Future Improvements



Potential improvements include:



\* Add rate limiting to API Gateway

\* Replace API-key authentication with Amazon Cognito or IAM authentication

\* Add Amazon CloudWatch alarms

\* Add structured application logging

\* Add monitoring dashboards

\* Add dead-letter handling for failed notifications

\* Add email templates

\* Add support for HTML emails

\* Add multiple notification channels such as SMS

\* Add integration tests against a deployed test environment

\* Introduce separate development and production Terraform environments

\* Add remote Terraform state using Amazon S3 with state locking

\* Add automated Terraform validation and security scanning to CI

\* Add dependency vulnerability scanning

\* Implement API Gateway throttling and usage plans



\---



\## What This Project Demonstrates



The project goes beyond simply deploying a Lambda function.



It demonstrates an end-to-end cloud engineering workflow:



```text

Application Development

&#x20;       ↓

Python + boto3

&#x20;       ↓

Automated Testing

&#x20;       ↓

pytest

&#x20;       ↓

Infrastructure as Code

&#x20;       ↓

Terraform

&#x20;       ↓

AWS Deployment

&#x20;       ↓

API Gateway → Lambda → SES

&#x20;       ↓

Secure Configuration

&#x20;       ↓

SSM + IAM

&#x20;       ↓

Continuous Integration

&#x20;       ↓

GitHub Actions

```



The result is a reproducible, tested and secure serverless notification platform managed through code.



\---



\## Author



\*\*Muse Jama\*\*



Cloud / DevOps Engineering Portfolio Project



Technologies:



```text

AWS | Terraform | Python | boto3 | pytest | GitHub Actions | IAM | API Gateway | Lambda | SES

```



