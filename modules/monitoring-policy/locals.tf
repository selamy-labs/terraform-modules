locals {
  scope_filter_parts = [
    for k, v in var.scope_labels : "resource.labels.${k} = \"${v}\""
  ]

  scope_suffix = length(local.scope_filter_parts) > 0 ? " AND ${join(" AND ", local.scope_filter_parts)}" : ""

  scoped_filters = {
    for i, c in var.conditions : i => "${c.filter}${local.scope_suffix}"
  }
}
