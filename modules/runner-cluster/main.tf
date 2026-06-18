locals {
  normalized_node_pools = {
    for name, pool in var.node_pools : name => {
      machine_class = pool.machine_class
      capacity_type = pool.capacity_type
      min_size      = pool.min_size
      max_size      = pool.max_size
      desired_size  = coalesce(pool.desired_size, pool.min_size)
      labels        = pool.labels
      taints        = pool.taints
      runner_labels = distinct(concat([name], pool.runner_labels))
    }
  }

  runner_labels = distinct(concat(
    var.runner_labels,
    flatten([for pool in values(local.normalized_node_pools) : pool.runner_labels])
  ))

  node_selector_labels = {
    for name, pool in local.normalized_node_pools : name => pool.labels
  }

  contract = {
    name                 = var.name
    provider_id          = var.provider_id
    kubeconfig           = var.kubeconfig
    node_pools           = local.normalized_node_pools
    runner_labels        = local.runner_labels
    node_selector_labels = local.node_selector_labels
    platform             = var.platform
    metadata             = var.metadata
  }
}
