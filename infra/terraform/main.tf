terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ============================================================
# Enable Required APIs
# ============================================================

resource "google_project_service" "alloydb" {
  service            = "alloydb.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "compute" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "servicenetworking" {
  service            = "servicenetworking.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "aiplatform" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

# ============================================================
# VPC Network Peering (Required for AlloyDB private networking)
# ============================================================

# Allocate an IP range for private services
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "sarathi-private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = "projects/${var.project_id}/global/networks/${var.network}"

  depends_on = [
    google_project_service.compute,
    google_project_service.servicenetworking,
  ]
}

# Create private connection for AlloyDB
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = "projects/${var.project_id}/global/networks/${var.network}"
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]

  depends_on = [
    google_project_service.servicenetworking,
  ]
}

# ============================================================
# AlloyDB Cluster & Instance
# ============================================================

resource "google_alloydb_cluster" "sarathi" {
  cluster_id = var.cluster_name
  location   = var.region
  network_config {
    network = "projects/${var.project_id}/global/networks/${var.network}"
  }
  
  initial_user {
    user     = "postgres"
    password = var.db_password
  }

  depends_on = [
    google_project_service.alloydb,
    google_service_networking_connection.private_vpc_connection,
  ]
}

# AlloyDB Primary Instance
resource "google_alloydb_instance" "primary" {
  cluster       = google_alloydb_cluster.sarathi.name
  instance_id   = var.instance_name
  instance_type = "PRIMARY"
  
  machine_config {
    cpu_count = var.cpu_count
  }

  database_flags = {
    # Enable pgvector for vector operations
    "alloydb.enable_pgvector" = "on"
    # Enable AlloyDB AI integration for Vertex AI
    "alloydb.enable_ai_integration" = "on"
  }
}

# ============================================================
# Outputs
# ============================================================

output "instance_ip" {
  value       = google_alloydb_instance.primary.ip_address
  description = "AlloyDB instance IP address"
}

output "connection_string" {
  value       = "postgresql://postgres:${var.db_password}@${google_alloydb_instance.primary.ip_address}:5432/sarathi"
  description = "Database connection string (for direct access via VPC)"
  sensitive   = true
}

output "cluster_name" {
  value       = google_alloydb_cluster.sarathi.name
  description = "AlloyDB cluster name"
}

output "alloydb_instance_uri" {
  value       = "projects/${var.project_id}/locations/${var.region}/clusters/${var.cluster_name}/instances/${var.instance_name}"
  description = "AlloyDB instance URI for the AlloyDB Connector (use in ALLOYDB_INSTANCE_URI env var)"
}

output "env_config" {
  value = <<-EOT
    # Add these to your backend/.env file:
    ALLOYDB_USE_CONNECTOR=true
    ALLOYDB_INSTANCE_URI=projects/${var.project_id}/locations/${var.region}/clusters/${var.cluster_name}/instances/${var.instance_name}
    ALLOYDB_HOST=${google_alloydb_instance.primary.ip_address}
    ALLOYDB_DATABASE=sarathi
    ALLOYDB_USER=postgres
    ALLOYDB_PASSWORD=<your-password>
    ALLOYDB_IAM_AUTH=false
    GOOGLE_CLOUD_PROJECT=${var.project_id}
    GOOGLE_CLOUD_REGION=${var.region}
  EOT
  description = "Environment variable configuration for backend"
  sensitive   = true
}
