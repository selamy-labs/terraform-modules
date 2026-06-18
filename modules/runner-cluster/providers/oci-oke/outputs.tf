output "cluster_contract" {
  description = "Provider-neutral runner-cluster contract."
  value       = module.contract.cluster_contract
}

output "kubeconfig" {
  description = "Kubeconfig reference for provider-neutral Kubernetes providers."
  value       = module.contract.kubeconfig
}

output "node_pools" {
  description = "Normalized node pools."
  value       = module.contract.node_pools
}

output "runner_labels" {
  description = "Distinct GitHub Actions runs-on labels exposed by this cluster."
  value       = module.contract.runner_labels
}

output "node_selector_labels" {
  description = "Node selector labels keyed by node pool name."
  value       = module.contract.node_selector_labels
}
