mock_provider "google" {}

variables {
  project_id   = "test-project-123456"
  display_name = "Disabled Alert"
  enabled      = false
  conditions = [
    {
      display_name    = "Dummy"
      filter          = "resource.type = \"k8s_container\""
      comparison      = "COMPARISON_GT"
      threshold_value = 1
      duration        = "60s"
    },
  ]
}

run "alert_can_be_disabled" {
  command = plan

  assert {
    condition     = google_monitoring_alert_policy.this.enabled == false
    error_message = "Expected alert to be disabled."
  }
}
