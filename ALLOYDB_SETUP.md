# AlloyDB Setup Guide for Tech Sarathi

This guide will help you set up AlloyDB on Google Cloud Platform for Tech Sarathi.

## Prerequisites

1. **Google Cloud Account** - [Sign up here](https://cloud.google.com/free)
2. **gcloud CLI** - [Install guide](https://cloud.google.com/sdk/docs/install)
3. **Billing enabled** on your GCP project
4. **PostgreSQL client** (psql) for database operations

## Cost Estimate

AlloyDB pricing (approximate):
- **Cluster**: ~$0.10/hour (~$73/month)
- **Instance (2 vCPU)**: ~$0.35/hour (~$255/month)
- **Storage**: ~$0.17/GB/month
- **Total**: ~$330-400/month for development

💡 **Tip**: Use the free trial credits ($300) or delete resources when not in use.

## Setup Steps

### Step 1: Install gcloud CLI

**Windows:**
```powershell
# Download and run the installer
# https://cloud.google.com/sdk/docs/install#windows
```

**Linux/Mac:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2: Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
```

### Step 3: Create or Select a Project

```bash
# Create new project
gcloud projects create tech-sarathi --name="Tech Sarathi"

# Or list existing projects
gcloud projects list

# Set active project
gcloud config set project tech-sarathi
```

### Step 4: Enable Billing

1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to Billing
3. Link a billing account to your project

### Step 5: Run the Setup Script

**Windows (PowerShell):**
```powershell
cd adk
.\setup-alloydb.ps1
```

**Linux/Mac:**
```bash
cd adk
chmod +x setup-alloydb.sh
./setup-alloydb.sh
```

The script will:
- Enable required APIs
- Create AlloyDB cluster
- Create primary instance
- Display connection details

⏱️ **This takes 10-15 minutes**

### Step 6: Configure Network Access

AlloyDB is private by default. You need to access it via:

**Option A: Cloud SQL Proxy (Recommended)**

```bash
# Download proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Run proxy
./cloud-sql-proxy --address 0.0.0.0 --port 5432 \
  projects/tech-sarathi/locations/asia-south1/clusters/sarathi-cluster/instances/sarathi-primary
```

**Option B: Compute Engine VM**

Create a VM in the same VPC and connect from there.

**Option C: VPN Connection**

Set up Cloud VPN to connect your local network to GCP VPC.

### Step 7: Create Database and Schema

```bash
# Connect to AlloyDB
psql -h <INSTANCE_IP> -U postgres

# Create database
CREATE DATABASE sarathi;

# Exit and reconnect to sarathi database
\q
psql -h <INSTANCE_IP> -U postgres -d sarathi

# Run schema
\i backend/db/schema.sql

# Load seed data (optional)
\i backend/db/seed.sql
```

### Step 8: Update Backend Configuration

Update `backend/.env`:

```env
ALLOYDB_HOST=<your-instance-ip>
ALLOYDB_DATABASE=sarathi
ALLOYDB_USER=postgres
ALLOYDB_PASSWORD=<your-password>
ALLOYDB_PORT=5432
```

### Step 9: Test Connection

```bash
cd backend
python -c "
from core.database import db
import asyncio

async def test():
    await db.connect()
    result = await db.fetchval('SELECT version()')
    print('Connected to:', result)
    await db.disconnect()

asyncio.run(test())
"
```

## Alternative: Quick Setup with Terraform

We've also provided Terraform configuration for automated setup:

```bash
cd adk/infra/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply configuration
terraform apply
```

## Managing AlloyDB

### View Cluster Status

```bash
gcloud alloydb clusters describe sarathi-cluster \
  --region=asia-south1
```

### View Instance Details

```bash
gcloud alloydb instances describe sarathi-primary \
  --cluster=sarathi-cluster \
  --region=asia-south1
```

### Create Backup

```bash
gcloud alloydb backups create sarathi-backup-$(date +%Y%m%d) \
  --cluster=sarathi-cluster \
  --region=asia-south1
```

### Scale Instance

```bash
gcloud alloydb instances update sarathi-primary \
  --cluster=sarathi-cluster \
  --region=asia-south1 \
  --cpu-count=4
```

## Cleanup (Delete Resources)

⚠️ **Warning**: This will delete all data!

```bash
# Delete instance
gcloud alloydb instances delete sarathi-primary \
  --cluster=sarathi-cluster \
  --region=asia-south1

# Delete cluster
gcloud alloydb clusters delete sarathi-cluster \
  --region=asia-south1
```

## Troubleshooting

### Cannot connect to AlloyDB

**Problem**: Connection timeout or refused
**Solution**: 
- Check if you're using Cloud SQL Proxy
- Verify VPC network configuration
- Ensure firewall rules allow connection

### Authentication failed

**Problem**: Password authentication failed
**Solution**:
- Verify password in .env file
- Reset password: `gcloud alloydb clusters update sarathi-cluster --password=NEW_PASSWORD`

### Schema creation fails

**Problem**: Permission denied or syntax errors
**Solution**:
- Ensure you're connected as postgres user
- Check PostgreSQL version compatibility (AlloyDB uses PostgreSQL 14+)

## Monitoring

### View Metrics in Console

1. Go to [AlloyDB Console](https://console.cloud.google.com/alloydb)
2. Select your cluster
3. View metrics: CPU, Memory, Connections, Query performance

### Set up Alerts

```bash
# Create alert for high CPU
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="AlloyDB High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s
```

## Best Practices

1. **Use Connection Pooling**: Already configured in `core/database.py`
2. **Enable Backups**: Set up automated daily backups
3. **Monitor Performance**: Use Cloud Monitoring
4. **Secure Credentials**: Use Secret Manager instead of .env in production
5. **Use Read Replicas**: For scaling read operations
6. **Regular Updates**: Keep AlloyDB version updated

## Cost Optimization

1. **Right-size instances**: Start with 2 vCPU, scale as needed
2. **Delete when not in use**: For development environments
3. **Use committed use discounts**: For production (up to 55% savings)
4. **Monitor storage**: Clean up old data and backups

## Support

- **GCP Documentation**: https://cloud.google.com/alloydb/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Support**: https://cloud.google.com/support

---

*Tech Sarathi - NIRMAN Hackathon 2026*
