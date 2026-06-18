module "contract" {
  source = "../.."

  name          = var.name
  provider_id   = "oci-oke"
  kubeconfig    = var.kubeconfig
  node_pools    = var.node_pools
  runner_labels = var.runner_labels
  platform      = var.platform
  metadata      = merge(var.metadata, { provider_module = "oci-oke" })
}
