variable "name" {
  description = "Logical runner cluster name used by platform consumers."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,62}$", var.name))
    error_message = "name must be a lowercase DNS-label style name."
  }
}

variable "provider_id" {
  description = "Cluster implementation behind this contract."
  type        = string

  validation {
    condition     = contains(["rackspace-spot", "oci-oke", "gke"], var.provider_id)
    error_message = "provider_id must be one of rackspace-spot, oci-oke, or gke."
  }
}

variable "kubeconfig" {
  description = "Reference to the kubeconfig consumed by the provider-neutral platform layer. This module carries references only, never secret material."
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

  validation {
    condition     = contains(["path", "secret_ref", "generated"], var.kubeconfig.source)
    error_message = "kubeconfig.source must be path, secret_ref, or generated."
  }
}

variable "node_pools" {
  description = "Provider-normalized node pools. Provider modules map their native pools into this shape."
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
    runner_labels = optional(list(string), [])
  }))

  validation {
    condition = alltrue([
      for pool in values(var.node_pools) :
      pool.min_size >= 0 && pool.max_size >= pool.min_size
    ])
    error_message = "Each node pool must have min_size >= 0 and max_size >= min_size."
  }

  validation {
    condition = alltrue([
      for pool in values(var.node_pools) :
      contains(["spot", "preemptible", "on-demand"], pool.capacity_type)
    ])
    error_message = "capacity_type must be spot, preemptible, or on-demand."
  }
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
