variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "nirman-project-493414"
}

variable "region" {
  description = "GCP region for AlloyDB"
  type        = string
  default     = "asia-south1"
}

variable "cluster_name" {
  description = "AlloyDB cluster name"
  type        = string
  default     = "sarathi-cluster"
}

variable "instance_name" {
  description = "AlloyDB instance name"
  type        = string
  default     = "sarathi-primary"
}

variable "network" {
  description = "VPC network name"
  type        = string
  default     = "default"
}

variable "cpu_count" {
  description = "Number of CPUs for the instance"
  type        = number
  default     = 2
}

variable "db_password" {
  description = "Database password for postgres user"
  type        = string
  sensitive   = true
}

variable "enable_iam_auth" {
  description = "Enable IAM-based authentication for AlloyDB"
  type        = bool
  default     = false
}
