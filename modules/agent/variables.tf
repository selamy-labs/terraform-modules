variable "project_id" {
  description = "GCP project ID that owns the agent credential secrets."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}

variable "agent_name" {
  description = "Canonical lowercase agent name, used for labels and default secret names."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}[a-z0-9]$", var.agent_name))
    error_message = "agent_name must be lowercase DNS-label style."
  }
}

variable "identity" {
  description = "Agent identity contract: human display, GitHub actor, commit attribution, and auth class."
  type = object({
    display_name     = string
    github_actor     = string
    committer_name   = string
    committer_email  = string
    auth_class       = string
    oauth_secret_ids = optional(list(string), [])
  })

  validation {
    condition     = contains(["committer-bot", "github-app", "oauth", "human-owner"], var.identity.auth_class)
    error_message = "identity.auth_class must be one of committer-bot, github-app, oauth, human-owner."
  }
}

variable "runtime" {
  description = "Hermes runtime shape for the agent. Kubernetes resources remain rendered by Helm/GitOps consumers."
  type = object({
    namespace            = string
    service_account_name = optional(string)
    hermes_image         = string
    os_user              = optional(string, "hermes")
    image_pull_secret    = optional(string, "ghcr-pull")
    resources = object({
      requests = map(string)
      limits   = map(string)
    })
    storage = object({
      class = string
      size  = string
    })
  })
}

variable "capabilities" {
  description = "Declared capabilities loaded into the agent runtime."
  type = object({
    skills = optional(list(string), [])
    mcp_servers = optional(map(object({
      enabled           = optional(bool, true)
      config_secret_ids = optional(list(string), [])
    })), {})
  })
  default = {}
}

variable "knowledge" {
  description = "Agent-owned memory/wiki surfaces and domains."
  type = object({
    memory_pvc    = optional(string)
    wiki_pvc      = optional(string)
    owned_domains = optional(list(string), [])
  })
  default = {}
}

variable "credentials" {
  description = "Credential secret declarations. Secret values are seeded out-of-band into GSM; this module creates secret shells and IAM only."
  type = map(object({
    remote_secret_id   = optional(string)
    target_secret_name = optional(string)
    create             = optional(bool, true)
    accessor_members   = optional(list(string), [])
    labels             = optional(map(string), {})
    keys = optional(list(object({
      secret_key      = string
      remote_property = optional(string)
    })), [])
  }))
  default = {}
}

variable "external_secret" {
  description = "ExternalSecrets contract defaults for Kubernetes consumers."
  type = object({
    store_name       = optional(string, "gcp-secret-manager")
    store_kind       = optional(string, "ClusterSecretStore")
    refresh_interval = optional(string, "1h")
  })
  default = {}
}

variable "cron" {
  description = "Recurring duties owned by the agent."
  type = map(object({
    schedule    = string
    command     = string
    suspend     = optional(bool, false)
    sla_minutes = optional(number)
  }))
  default = {}
}

variable "lane" {
  description = "Queue and issue sources this agent drains."
  type = object({
    queue_name       = optional(string)
    priority_sources = optional(list(string), [])
    issue_repos      = optional(list(string), [])
  })
  default = {}
}

variable "guardrails" {
  description = "Enforcement hooks and policy limits that define what the agent may not do."
  type = object({
    enforcement_hooks  = optional(list(string), [])
    approvals_required = optional(list(string), [])
    forbidden_actions = optional(list(string), [
      "imperative-infra-mutation",
      "print-secret-values",
    ])
  })
  default = {}
}

variable "create_gsm_secrets" {
  description = "When true, create Google Secret Manager secret shells for credentials with create=true."
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels applied to created GSM secrets."
  type        = map(string)
  default     = {}
}
