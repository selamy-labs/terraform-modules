variable "name" {
  description = "Release name and runner scale-set name. Must be unique per ARC controller installation (a label cannot run in two scale sets at once)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", var.name))
    error_message = "name must be a lowercase RFC1123 label (a-z, 0-9, -)."
  }
}

variable "namespace" {
  description = "Kubernetes namespace for the runner scale set."
  type        = string
  default     = "github-runners"
}

variable "chart_version" {
  description = "Version of the upstream gha-runner-scale-set chart (pin explicitly; must match the installed controller)."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+$", var.chart_version))
    error_message = "chart_version must be a pinned semver (e.g. 0.12.1)."
  }
}

variable "github_config_url" {
  description = "GitHub org or repo URL the runners attach to (e.g. https://github.com/selamy-labs)."
  type        = string

  validation {
    condition     = can(regex("^https://github\\.com/.+", var.github_config_url))
    error_message = "github_config_url must be a https://github.com/... URL."
  }
}

variable "github_config_secret" {
  description = "Name of the pre-existing Kubernetes Secret holding GitHub App / PAT auth for ARC (created out-of-band, e.g. via ExternalSecrets)."
  type        = string
}

variable "controller_service_account_name" {
  description = "Name of the ARC controller ServiceAccount."
  type        = string
  default     = "arc-gha-rs-controller"
}

variable "controller_service_account_namespace" {
  description = "Namespace of the ARC controller ServiceAccount."
  type        = string
  default     = "arc-systems"
}

variable "runner_group" {
  description = "GitHub runner group the scale set joins."
  type        = string
  default     = "Default"
}

variable "min_runners" {
  description = "Minimum idle runners (0 = scale-to-zero)."
  type        = number
  default     = 0

  validation {
    condition     = var.min_runners >= 0
    error_message = "min_runners must be >= 0."
  }
}

variable "max_runners" {
  description = "Maximum concurrent runners."
  type        = number
  default     = 2

  validation {
    condition     = var.max_runners >= 1
    error_message = "max_runners must be >= 1."
  }
}

variable "runner_image" {
  description = "Runner container image."
  type        = string
  default     = "ghcr.io/actions/actions-runner:latest"
}

variable "runner_resources" {
  description = "Runner container resource requests/limits."
  type = object({
    requests = optional(map(string), { cpu = "250m", memory = "512Mi" })
    limits   = optional(map(string), { cpu = "1", memory = "2Gi" })
  })
  default = {}
}

variable "extra_values" {
  description = "Additional raw Helm values (YAML string) merged last, for escape-hatch overrides. Keep empty in the common case."
  type        = string
  default     = ""
}

variable "create_namespace" {
  description = "Whether the helm_release should create the namespace."
  type        = bool
  default     = true
}
