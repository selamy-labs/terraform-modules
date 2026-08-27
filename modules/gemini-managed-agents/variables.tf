variable "project_id" {
  description = "Google Cloud project used by the Gemini Developer API."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid Google Cloud project ID."
  }
}

variable "manifest_paths" {
  description = "Stable keys mapped to normalized managed-agent JSON manifests. Paths may be absolute or relative to the root module."
  type        = map(string)

  validation {
    condition     = alltrue([for key, path in var.manifest_paths : can(regex("^[a-z][a-z0-9_-]*$", key)) && trimspace(path) != ""])
    error_message = "Every manifest_paths entry must have a stable lowercase key and non-empty path. Use an empty map to retire the final declared revision before removing the module block."
  }
}

variable "authentication" {
  description = "API authentication. OAuth is preferred. API keys must be referenced by an immutable Secret Manager version and are read only by the reconciler at runtime."
  type = object({
    mode                           = optional(string, "oauth")
    api_key_secret_manager_version = optional(string)
  })
  default = {}

  validation {
    condition = contains(["oauth", "api_key_secret_manager"], var.authentication.mode) && (
      var.authentication.mode == "oauth" || try(can(regex("^projects/[^/]+/secrets/[^/]+/versions/[0-9]+$", var.authentication.api_key_secret_manager_version)), false)
    )
    error_message = "authentication.mode must be oauth or api_key_secret_manager; key mode requires an immutable projects/.../secrets/.../versions/<number> reference."
  }
}

variable "enable_remote_read" {
  description = "Read each remote revision during refresh and report missing or drifted agents. Disable only for offline validation and tests."
  type        = bool
  default     = true
}

variable "python_executable" {
  description = "Python 3.11+ executable used by the mechanical reconciler."
  type        = string
  default     = "python3"

  validation {
    condition     = can(regex("^[A-Za-z0-9_./-]+$", var.python_executable))
    error_message = "python_executable may contain only path-safe characters."
  }
}
