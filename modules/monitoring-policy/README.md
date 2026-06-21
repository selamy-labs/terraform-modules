# monitoring-policy

Creates a Google Cloud Monitoring alert policy scoped by label. Cloud policy only (no k8s workload objects).

## Usage

```hcl
module "my_alert" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/monitoring-policy?ref=v0.2.0"

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

documentation = {
  content = "Investigate the workload before declaring the alert healthy."
}
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_google"></a> [google](#requirement\_google) | >= 5.0, < 7.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | >= 5.0, < 7.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_monitoring_alert_policy.this](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_alert_policy) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_conditions"></a> [conditions](#input\_conditions) | List of alert conditions. Defaults to threshold conditions; set condition_type="absent" for condition_absent. | <pre>list(object({<br/>    display_name         = string<br/>    filter               = string<br/>    condition_type       = optional(string, "threshold")<br/>    comparison           = optional(string)<br/>    threshold_value      = optional(number)<br/>    duration             = string<br/>    alignment_period     = optional(string, "60s")<br/>    per_series_aligner   = optional(string, "ALIGN_RATE")<br/>    cross_series_reducer = optional(string, "REDUCE_NONE")<br/>    group_by_fields      = optional(list(string), [])<br/>    trigger_count        = optional(number, 1)<br/>  }))</pre> | n/a | yes |
| <a name="input_display_name"></a> [display\_name](#input\_display\_name) | Display name for the alert policy. | `string` | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_auto_close_duration"></a> [auto\_close\_duration](#input\_auto\_close\_duration) | Auto-close duration (e.g. 86400s). Null to omit. | `string` | `null` | no |
| <a name="input_combiner"></a> [combiner](#input\_combiner) | How to combine conditions: OR, AND, AND\_WITH\_MATCHING\_RESOURCE. | `string` | `"OR"` | no |
| <a name="input_documentation"></a> [documentation](#input\_documentation) | Optional alert documentation block. | <pre>object({<br/>    content   = string<br/>    mime_type = optional(string, "text/markdown")<br/>  })</pre> | `null` | no |
| <a name="input_enabled"></a> [enabled](#input\_enabled) | Whether the alert policy is enabled. | `bool` | `true` | no |
| <a name="input_labels"></a> [labels](#input\_labels) | User labels for the alert policy. | `map(string)` | `{}` | no |
| <a name="input_notification_channels"></a> [notification\_channels](#input\_notification\_channels) | List of notification channel IDs. | `list(string)` | `[]` | no |
| <a name="input_scope_labels"></a> [scope\_labels](#input\_scope\_labels) | Map of label keys to values used to scope the alert filter (e.g. {container\_name = "my-app"}). Appended as AND clauses to each condition's filter. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_alert_policy_id"></a> [alert\_policy\_id](#output\_alert\_policy\_id) | The ID of the alert policy. |
| <a name="output_creation_record"></a> [creation\_record](#output\_creation\_record) | Creation record of the alert policy. |
<!-- END_TF_DOCS -->
