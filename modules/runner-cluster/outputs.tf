output "cluster_contract" {
  description = "Provider-neutral runner-cluster contract consumed by ARC, ArgoCD, and tenant registry platform layers."
  value       = local.contract
}

output "kubeconfig" {
  description = "Kubeconfig reference for provider-neutral Kubernetes providers. Contains references only, not secret values."
  value       = var.kubeconfig
}

output "node_pools" {
  description = "Normalized node pools with standard labels and runner capability labels."
  value       = local.normalized_node_pools
}

output "runner_labels" {
  description = "Distinct GitHub Actions runs-on labels exposed by this cluster."
  value       = local.runner_labels
}

output "node_selector_labels" {
  description = "Node selector labels keyed by node pool name for runner scale set consumers."
  value       = local.node_selector_labels
}
