variable "project_id" {
  description = "GCP project ID."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}

variable "account_id" {
  description = "The service account ID (the part before @)."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.account_id))
    error_message = "account_id must be 6-30 lowercase letters, digits, or hyphens."
  }
}

variable "display_name" {
  description = "Human-readable display name for the service account."
  type        = string
  default     = ""
}

variable "description" {
  description = "Description of the service account."
  type        = string
  default     = ""
}

variable "wif_pool_provider" {
  description = "Full resource name of the Workload Identity pool provider (projects/NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER)."
  type        = string
  default     = null
}

variable "wif_k8s_namespace" {
  description = "Kubernetes namespace for WIF binding."
  type        = string
  default     = null
}

variable "wif_k8s_service_account" {
  description = "Kubernetes service account name for WIF binding."
  type        = string
  default     = null
}

variable "additional_wif_members" {
  description = "Extra IAM members to grant workloadIdentityUser on this SA."
  type        = list(string)
  default     = []
}

variable "project_roles" {
  description = "List of IAM roles to grant to this SA at the project level."
  type        = list(string)
  default     = []
}
