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

# Enable required APIs
resource "google_project_service" "alloydb" {
  service = "alloydb.googleapis.com"
}

resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "servicenetworking" {
  service = "servicenetworking.googleapis.com"
}

resource "google_project_service" "aiplatform" {
  service = "aiplatform.googleapis.com"
}

# AlloyDB Cluster
resource "google_alloydb_cluster" "sarathi" {
  cluster_id = var.cluster_name
  location   = var.region
  network    = "projects/${var.project_id}/global/networks/${var.network}"
  
  initial_user {
    user     = "postgres"
    password = var.db_password
  }

  depends_on = [
    google_project_service.alloydb
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
}

# Output connection details
output "instance_ip" {
  value       = google_alloydb_instance.primary.ip_address
  description = "AlloyDB instance IP address"
}

output "connection_string" {
  value       = "postgresql://postgres:${var.db_password}@${google_alloydb_instance.primary.ip_address}:5432/sarathi"
  description = "Database connection string"
  sensitive   = true
}

output "cluster_name" {
  value       = google_alloydb_cluster.sarathi.name
  description = "AlloyDB cluster name"
}
