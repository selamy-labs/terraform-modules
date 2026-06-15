output "email" {
  description = "The service account email."
  value       = google_service_account.this.email
}

output "name" {
  description = "The fully-qualified service account resource name."
  value       = google_service_account.this.name
}

output "unique_id" {
  description = "The unique numeric ID of the service account."
  value       = google_service_account.this.unique_id
}

output "member" {
  description = "The IAM member string for this service account."
  value       = "serviceAccount:${google_service_account.this.email}"
}
