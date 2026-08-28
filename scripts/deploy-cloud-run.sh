#!/bin/bash
# ==============================================================================
# ARCHON: Cloud Run Deployment Script
# Deploys FastAPI Backend to Google Cloud Run
# ==============================================================================

set -e

PROJECT_ID="${GCP_PROJECT_ID:-archon-enterprise-fleet}"
REGION="${GCP_LOCATION:-us-central1}"
SERVICE_NAME="archon-backend"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "======================================================================"
echo "  Deploying ARCHON Backend to Google Cloud Run"
echo "  Project: ${PROJECT_ID} | Region: ${REGION}"
echo "======================================================================"

# Ensure Google Cloud SDK is authenticated
gcloud config set project "${PROJECT_ID}"

# Submit container build via Google Cloud Build
echo "[1/3] Building container image via Cloud Build..."
gcloud builds submit backend --tag "${IMAGE_TAG}"

# Deploy to Cloud Run
echo "[2/3] Deploying service to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GOOGLE_API_KEY=${GOOGLE_API_KEY},USE_MEMORY_BANK=true,USE_MODEL_ARMOR=true,APPROVAL_THRESHOLD=10000" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --port 8000

echo "[3/3] Deployment complete!"
URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')
echo "Service live at: ${URL}"
echo "Health Check: ${URL}/health"
echo "API Docs: ${URL}/docs"
