mock_provider "google" {}

variables {
  project_id   = "test-project-123456"
  display_name = "Absent heartbeat"
  documentation = {
    content = "Investigate pod readiness before declaring the agent healthy."
  }
  conditions = [
    {
      display_name         = "No heartbeat"
      condition_type       = "absent"
      filter               = "resource.type = \"k8s_container\" AND metric.type = \"kubernetes.io/container/uptime\""
      duration             = "300s"
      alignment_period     = "60s"
      per_series_aligner   = "ALIGN_MEAN"
      cross_series_reducer = "REDUCE_COUNT"
      group_by_fields      = ["resource.label.pod_name"]
    },
  ]
}

run "renders_absent_condition_and_documentation" {
  command = plan

  assert {
    condition     = google_monitoring_alert_policy.this.documentation[0].content == "Investigate pod readiness before declaring the agent healthy."
    error_message = "Expected alert documentation to render."
  }

  assert {
    condition     = google_monitoring_alert_policy.this.documentation[0].mime_type == "text/markdown"
    error_message = "Expected default markdown documentation mime type."
  }

  assert {
    condition     = length(google_monitoring_alert_policy.this.conditions[0].condition_absent) == 1
    error_message = "Expected one absent condition."
  }
}
