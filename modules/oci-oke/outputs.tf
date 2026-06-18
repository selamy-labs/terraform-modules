output "cluster_id" {
  description = "OKE cluster OCID."
  value       = oci_containerengine_cluster.this.id
}

output "cluster_name" {
  description = "OKE cluster name."
  value       = oci_containerengine_cluster.this.name
}

output "vcn_id" {
  description = "VCN OCID."
  value       = oci_core_vcn.this.id
}

output "api_subnet_id" {
  description = "Kubernetes API endpoint subnet OCID."
  value       = oci_core_subnet.api.id
}

output "node_subnet_id" {
  description = "Worker node subnet OCID."
  value       = oci_core_subnet.nodes.id
}

output "pod_subnet_id" {
  description = "Pod subnet OCID."
  value       = oci_core_subnet.pods.id
}

output "preemptible_node_pool_id" {
  description = "Preemptible node pool OCID."
  value       = oci_containerengine_node_pool.preemptible.id
}

output "fallback_node_pool_id" {
  description = "Fallback on-demand node pool OCID, when enabled."
  value       = try(oci_containerengine_node_pool.fallback[0].id, null)
}
