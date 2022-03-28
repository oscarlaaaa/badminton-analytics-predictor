#!/bin/bash
echo "Logging into AWS..."
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com

echo "Building image..."
docker build -t ${IMAGE_NAME} . --no-cache

echo "Deploying image..."
docker tag  ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/${IMAGE_NAME}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest 