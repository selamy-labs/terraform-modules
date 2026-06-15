# monitoring-policy

Creates a Google Cloud Monitoring alert policy scoped by label. Cloud policy only (no k8s workload objects).

## Usage

```hcl
module "my_alert" {
  source = "github.com/selamy-labs/terraform-modules//modules/monitoring-policy"

  project_id   = "my-project"
  display_name = "High CPU - my-app"

  scope_labels = { container_name = "my-app" }

  conditions = [{
    display_name    = "CPU > 80%"
    filter          = "resource.type = \"k8s_container\" AND metric.type = \"kubernetes.io/container/cpu/limit_utilization\""
    comparison      = "COMPARISON_GT"
    threshold_value = 0.8
    duration        = "300s"
  }]
}
```

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
