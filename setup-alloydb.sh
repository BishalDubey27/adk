#!/bin/bash

# Tech Sarathi - AlloyDB Setup Script
# This script provisions AlloyDB on Google Cloud Platform

set -e

echo "🚀 Tech Sarathi - AlloyDB Setup"
echo "================================"
echo ""

# Configuration
PROJECT_ID="tech-sarathi"
REGION="asia-south1"
CLUSTER_NAME="sarathi-cluster"
INSTANCE_NAME="sarathi-primary"
NETWORK="default"
PASSWORD=""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Prompt for project ID
read -p "Enter your GCP Project ID (default: tech-sarathi): " input_project
PROJECT_ID=${input_project:-$PROJECT_ID}

# Prompt for region
read -p "Enter region (default: asia-south1): " input_region
REGION=${input_region:-$REGION}

# Prompt for password
while [ -z "$PASSWORD" ]; do
    read -sp "Enter database password: " PASSWORD
    echo ""
    if [ -z "$PASSWORD" ]; then
        echo "❌ Password cannot be empty"
    fi
done

echo ""
echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Cluster: $CLUSTER_NAME"
echo "   Instance: $INSTANCE_NAME"
echo ""

read -p "Continue with setup? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Setup cancelled"
    exit 0
fi

echo ""
echo "🔧 Setting up Google Cloud project..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable alloydb.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable aiplatform.googleapis.com

echo "✅ APIs enabled"
echo ""

# Create AlloyDB cluster
echo "🗄️  Creating AlloyDB cluster (this takes ~10-15 minutes)..."
gcloud alloydb clusters create $CLUSTER_NAME \
    --region=$REGION \
    --network=$NETWORK \
    --password=$PASSWORD \
    --project=$PROJECT_ID

echo "✅ Cluster created"
echo ""

# Create primary instance
echo "💾 Creating primary instance..."
gcloud alloydb instances create $INSTANCE_NAME \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --instance-type=PRIMARY \
    --cpu-count=2 \
    --project=$PROJECT_ID

echo "✅ Instance created"
echo ""

# Get connection details
echo "📝 Getting connection details..."
INSTANCE_IP=$(gcloud alloydb instances describe $INSTANCE_NAME \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --format="value(ipAddress)")

echo ""
echo "✅ AlloyDB Setup Complete!"
echo "=========================="
echo ""
echo "Connection Details:"
echo "  Host: $INSTANCE_IP"
echo "  Port: 5432"
echo "  Database: postgres"
echo "  User: postgres"
echo "  Password: [your password]"
echo ""
echo "📝 Update your backend/.env file with:"
echo ""
echo "ALLOYDB_HOST=$INSTANCE_IP"
echo "ALLOYDB_DATABASE=sarathi"
echo "ALLOYDB_USER=postgres"
echo "ALLOYDB_PASSWORD=$PASSWORD"
echo ""
echo "Next steps:"
echo "1. Create the 'sarathi' database"
echo "2. Run the schema: psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/schema.sql"
echo "3. Load seed data: psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/seed.sql"
echo ""
