module "example_alert" {
  source = "../../"

  project_id   = "my-gcp-project"
  display_name = "High CPU - my-app"

  scope_labels = {
    container_name = "my-app"
  }

  conditions = [
    {
      display_name    = "CPU utilization > 80%"
      filter          = "resource.type = \"k8s_container\" AND metric.type = \"kubernetes.io/container/cpu/limit_utilization\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      duration        = "300s"
    },
  ]

  auto_close_duration = "86400s"
}

output "alert_id" {
  value = module.example_alert.alert_policy_id
}
