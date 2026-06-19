variable "project_id" {
  description = "GCP project ID."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}

variable "secret_id" {
  description = "The secret ID within Secret Manager."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]{1,255}$", var.secret_id))
    error_message = "secret_id must match [a-zA-Z0-9_-]{1,255}."
  }
}

variable "secret_data" {
  description = "Optional secret payload. When null, only the secret resource is created (no version)."
  type        = string
  default     = null
  sensitive   = true
}

variable "accessor_members" {
  description = "List of IAM members granted secretmanager.secretAccessor (e.g. serviceAccount:x@proj.iam.gserviceaccount.com)."
  type        = list(string)
  default     = []
}

variable "named_accessor_members" {
  description = "Map of stable IAM member keys to members granted secretmanager.secretAccessor. Use when migrating existing singleton IAM resources without changing Terraform addresses."
  type        = map(string)
  default     = {}
}

variable "version_adder_members" {
  description = "Map of stable IAM member keys to members granted secretmanager.secretVersionAdder."
  type        = map(string)
  default     = {}
}

variable "labels" {
  description = "Labels to attach to the secret."
  type        = map(string)
  default     = {}
}
