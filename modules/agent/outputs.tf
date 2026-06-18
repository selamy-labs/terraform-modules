output "agent_contract" {
  description = "Normalized agent/employee contract for Helm, GitOps, and drift-review consumers."
  value       = local.agent_contract
}

output "credential_secret_ids" {
  description = "Credential name to GSM secret ID map."
  value       = local.credential_secret_ids
}

output "credential_secret_names" {
  description = "Credential name to GSM resource name map for secrets created by this module."
  value = {
    for name, secret in google_secret_manager_secret.credentials :
    name => secret.name
  }
}

output "external_secret_specs" {
  description = "Normalized ExternalSecret sync specs for Kubernetes chart consumers."
  value       = local.external_secret_specs
}
