variable "name" {
  description = "Logical runner cluster name."
  type        = string
}

variable "kubeconfig" {
  description = "Reference to the OKE kubeconfig. Contains references only, not secret values."
  type = object({
    source  = string
    context = optional(string)
    path    = optional(string)
    secret_ref = optional(object({
      project_id = string
      secret_id  = string
      version    = optional(string, "latest")
      key        = optional(string)
    }))
  })
}

variable "node_pools" {
  description = "OKE node pools normalized to the runner-cluster contract."
  type = map(object({
    machine_class = string
    capacity_type = string
    min_size      = number
    max_size      = number
    desired_size  = optional(number)
    labels        = map(string)
    taints = optional(list(object({
      key    = string
      value  = optional(string)
      effect = string
    })), [])
    runner_labels  = optional(list(string), [])
    ocid           = optional(string)
    compartment_id = optional(string)
  }))
}

variable "runner_labels" {
  description = "Global GitHub Actions runs-on labels exposed by this cluster."
  type        = list(string)
  default     = []
}

variable "platform" {
  description = "Provider-neutral platform defaults layered onto the cluster by the consumer."
  type = object({
    arc_namespace       = optional(string, "arc-runners")
    argocd_namespace    = optional(string, "argocd")
    tenant_registry_ref = optional(string)
  })
  default = {}
}

variable "metadata" {
  description = "Free-form metadata for ADR links, rollout notes, and ownership."
  type        = map(string)
  default     = {}
}
