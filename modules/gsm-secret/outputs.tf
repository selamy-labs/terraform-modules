output "secret_id" {
  description = "The fully-qualified secret ID."
  value       = google_secret_manager_secret.this.id
}

output "secret_name" {
  description = "The secret resource name (projects/*/secrets/*)."
  value       = google_secret_manager_secret.this.name
}

output "version_id" {
  description = "The secret version ID, if a version was created."
  value       = try(google_secret_manager_secret_version.this[0].id, null)
}
