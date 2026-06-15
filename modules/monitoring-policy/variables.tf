variable "project_id" {
  description = "GCP project ID."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}

variable "display_name" {
  description = "Display name for the alert policy."
  type        = string
}

variable "combiner" {
  description = "How to combine conditions: OR, AND, AND_WITH_MATCHING_RESOURCE."
  type        = string
  default     = "OR"

  validation {
    condition     = contains(["OR", "AND", "AND_WITH_MATCHING_RESOURCE"], var.combiner)
    error_message = "combiner must be OR, AND, or AND_WITH_MATCHING_RESOURCE."
  }
}

variable "enabled" {
  description = "Whether the alert policy is enabled."
  type        = bool
  default     = true
}

variable "scope_labels" {
  description = "Map of label keys to values used to scope the alert filter (e.g. {container_name = \"my-app\"}). Appended as AND clauses to each condition's filter."
  type        = map(string)
  default     = {}
}

variable "conditions" {
  description = "List of alert conditions."
  type = list(object({
    display_name         = string
    filter               = string
    comparison           = string
    threshold_value      = number
    duration             = string
    alignment_period     = optional(string, "60s")
    per_series_aligner   = optional(string, "ALIGN_RATE")
    cross_series_reducer = optional(string, "REDUCE_NONE")
    group_by_fields      = optional(list(string), [])
    trigger_count        = optional(number, 1)
  }))
}

variable "notification_channels" {
  description = "List of notification channel IDs."
  type        = list(string)
  default     = []
}

variable "auto_close_duration" {
  description = "Auto-close duration (e.g. 86400s). Null to omit."
  type        = string
  default     = null
}

variable "labels" {
  description = "User labels for the alert policy."
  type        = map(string)
  default     = {}
}
