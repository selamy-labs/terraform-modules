output "alert_policy_id" {
  description = "The ID of the alert policy."
  value       = google_monitoring_alert_policy.this.name
}

output "creation_record" {
  description = "Creation record of the alert policy."
  value       = google_monitoring_alert_policy.this.creation_record
}
