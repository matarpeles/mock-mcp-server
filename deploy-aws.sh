#!/bin/bash
set -e

# Configuration
AWS_REGION="eu-west-1"
APP_NAME="mock-mcp-server"
ECR_REPO_NAME="mock-mcp-server"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Deploying Mock MCP Server to AWS App Runner"
echo "Account: $ACCOUNT_ID | Region: $AWS_REGION"

# 1. Create ECR repository (if not exists)
echo "📦 Creating ECR repository..."
aws ecr create-repository \
  --repository-name $ECR_REPO_NAME \
  --region $AWS_REGION 2>/dev/null || echo "Repository already exists"

# 2. Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 3. Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t $ECR_REPO_NAME .

echo "📤 Pushing to ECR..."
docker tag $ECR_REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# 4. Create App Runner service
echo "🏃 Creating App Runner service..."
aws apprunner create-service \
  --service-name $APP_NAME \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/'$ECR_REPO_NAME':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "ANTHROPIC_API_KEY": "'$ANTHROPIC_API_KEY'"
        }
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::'$ACCOUNT_ID':role/AppRunnerECRAccessRole"
    }
  }' \
  --instance-configuration '{
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }' \
  --region $AWS_REGION

echo "✅ Deployment initiated! Check AWS Console for status."
echo "URL will be: https://<service-id>.$AWS_REGION.awsapprunner.com/datadog/mcp"
