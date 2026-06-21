resource "google_monitoring_alert_policy" "this" {
  project      = var.project_id
  display_name = var.display_name
  combiner     = var.combiner
  enabled      = var.enabled

  user_labels = var.labels

  dynamic "documentation" {
    for_each = var.documentation != null ? [var.documentation] : []
    content {
      content   = documentation.value.content
      mime_type = try(documentation.value.mime_type, "text/markdown")
    }
  }

  dynamic "conditions" {
    for_each = var.conditions
    content {
      display_name = conditions.value.display_name

      dynamic "condition_threshold" {
        for_each = try(conditions.value.condition_type, "threshold") == "threshold" ? [conditions.value] : []
        content {
          filter          = local.scoped_filters[conditions.key]
          comparison      = condition_threshold.value.comparison
          threshold_value = condition_threshold.value.threshold_value
          duration        = condition_threshold.value.duration

          aggregations {
            alignment_period     = try(condition_threshold.value.alignment_period, "60s")
            per_series_aligner   = try(condition_threshold.value.per_series_aligner, "ALIGN_RATE")
            cross_series_reducer = try(condition_threshold.value.cross_series_reducer, "REDUCE_NONE")
            group_by_fields      = try(condition_threshold.value.group_by_fields, [])
          }

          trigger {
            count = try(condition_threshold.value.trigger_count, 1)
          }
        }
      }

      dynamic "condition_absent" {
        for_each = try(conditions.value.condition_type, "threshold") == "absent" ? [conditions.value] : []
        content {
          filter   = local.scoped_filters[conditions.key]
          duration = condition_absent.value.duration

          aggregations {
            alignment_period     = try(condition_absent.value.alignment_period, "60s")
            per_series_aligner   = try(condition_absent.value.per_series_aligner, "ALIGN_RATE")
            cross_series_reducer = try(condition_absent.value.cross_series_reducer, "REDUCE_NONE")
            group_by_fields      = try(condition_absent.value.group_by_fields, [])
          }

          trigger {
            count = try(condition_absent.value.trigger_count, 1)
          }
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
