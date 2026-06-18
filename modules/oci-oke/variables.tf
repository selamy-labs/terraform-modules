variable "compartment_id" {
  description = "OCI compartment OCID for all OKE experiment resources."
  type        = string
}

variable "name" {
  description = "Short resource prefix for the OKE experiment."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,40}$", var.name))
    error_message = "name must be 3-41 lowercase letters, numbers, or hyphens, starting with a letter."
  }
}

variable "kubernetes_version" {
  description = "OKE Kubernetes version, for example v1.31.1."
  type        = string
}

variable "availability_domain" {
  description = "OCI availability domain name used for the initial side-by-side experiment node pools."
  type        = string
}

variable "vcn_cidr" {
  description = "VCN CIDR block."
  type        = string
  default     = "10.80.0.0/16"
}

variable "api_subnet_cidr" {
  description = "Public subnet for the Kubernetes API endpoint."
  type        = string
  default     = "10.80.0.0/24"
}

variable "lb_subnet_cidr" {
  description = "Public subnet for Kubernetes load balancers."
  type        = string
  default     = "10.80.1.0/24"
}

variable "node_subnet_cidr" {
  description = "Private subnet for OKE worker nodes."
  type        = string
  default     = "10.80.10.0/24"
}

variable "pod_subnet_cidr" {
  description = "Private subnet used by OCI VCN-native pod networking."
  type        = string
  default     = "10.80.20.0/22"
}

variable "service_cidr" {
  description = "Kubernetes service CIDR."
  type        = string
  default     = "10.96.0.0/16"
}

variable "pods_cidr" {
  description = "Kubernetes pods CIDR used by the OKE cluster record."
  type        = string
  default     = "10.244.0.0/16"
}

variable "public_endpoint_enabled" {
  description = "Expose the Kubernetes API endpoint publicly for the experiment. Restrict with endpoint_allowed_cidrs."
  type        = bool
  default     = true
}

variable "endpoint_allowed_cidrs" {
  description = "CIDRs allowed to reach the public Kubernetes API endpoint."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_image_id" {
  description = "OKE worker node image OCID. Keep explicit so applies are reproducible."
  type        = string
}

variable "boot_volume_size_gb" {
  description = "Boot volume size for worker nodes."
  type        = number
  default     = 100
}

variable "preemptible_node_shape" {
  description = "OCI compute shape for preemptible runner nodes."
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "preemptible_ocpus" {
  description = "OCPUs for each preemptible flex node."
  type        = number
  default     = 2
}

variable "preemptible_memory_gb" {
  description = "Memory for each preemptible flex node."
  type        = number
  default     = 16
}

variable "preemptible_node_count" {
  description = "Initial preemptible node count. Use min>=1 for the side-by-side runner experiment."
  type        = number
  default     = 1
}

variable "fallback_node_shape" {
  description = "OCI compute shape for on-demand fallback runner nodes."
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "fallback_ocpus" {
  description = "OCPUs for each fallback flex node."
  type        = number
  default     = 2
}

variable "fallback_memory_gb" {
  description = "Memory for each fallback flex node."
  type        = number
  default     = 16
}

variable "fallback_node_count" {
  description = "Initial on-demand fallback node count. Use min>=1 so fallback capacity is tested."
  type        = number
  default     = 1
}

variable "enable_fallback_pool" {
  description = "Create the on-demand fallback node pool."
  type        = bool
  default     = true
}

variable "freeform_tags" {
  description = "Freeform tags applied to OCI resources."
  type        = map(string)
  default     = {}
}
