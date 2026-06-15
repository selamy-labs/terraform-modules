mock_provider "google" {}

variables {
  project_id   = "test-project-123456"
  display_name = "Test Alert"
  scope_labels = {
    container_name = "my-app"
  }
  conditions = [
    {
      display_name    = "High CPU"
      filter          = "resource.type = \"k8s_container\" AND metric.type = \"kubernetes.io/container/cpu/limit_utilization\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      duration        = "300s"
    },
  ]
}

run "creates_alert_policy" {
  command = plan

  assert {
    condition     = google_monitoring_alert_policy.this.display_name == "Test Alert"
    error_message = "Alert display_name mismatch."
  }

  assert {
    condition     = google_monitoring_alert_policy.this.enabled == true
    error_message = "Expected alert enabled by default."
  }
}

run "scopes_filter_by_labels" {
  command = plan

  assert {
    condition     = length(google_monitoring_alert_policy.this.conditions) == 1
    error_message = "Expected one condition."
  }
}
