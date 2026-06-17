output "release_name" {
  description = "The Helm release name (== the runner scale-set name / GitHub runner label)."
  value       = helm_release.this.name
}

output "namespace" {
  description = "Namespace the runner scale set is deployed into."
  value       = helm_release.this.namespace
}

output "chart_version" {
  description = "The deployed gha-runner-scale-set chart version."
  value       = helm_release.this.version
}

output "status" {
  description = "Status of the Helm release."
  value       = helm_release.this.status
}
