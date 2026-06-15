resource "google_monitoring_alert_policy" "this" {
  project      = var.project_id
  display_name = var.display_name
  combiner     = var.combiner
  enabled      = var.enabled

  user_labels = var.labels

  dynamic "conditions" {
    for_each = var.conditions
    content {
      display_name = conditions.value.display_name

      condition_threshold {
        filter          = local.scoped_filters[conditions.key]
        comparison      = conditions.value.comparison
        threshold_value = conditions.value.threshold_value
        duration        = conditions.value.duration

        aggregations {
          alignment_period     = try(conditions.value.alignment_period, "60s")
          per_series_aligner   = try(conditions.value.per_series_aligner, "ALIGN_RATE")
          cross_series_reducer = try(conditions.value.cross_series_reducer, "REDUCE_NONE")
          group_by_fields      = try(conditions.value.group_by_fields, [])
        }

        trigger {
          count = try(conditions.value.trigger_count, 1)
        }
      }
    }
  }

  dynamic "alert_strategy" {
    for_each = var.auto_close_duration != null ? [true] : []
    content {
      auto_close = var.auto_close_duration
    }
  }

  notification_channels = var.notification_channels
}
