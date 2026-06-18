run "normalizes_runner_cluster_contract" {
  command = plan

  variables {
    name        = "speedforge-runners"
    provider_id = "oci-oke"
    kubeconfig = {
      source = "secret_ref"
      secret_ref = {
        project_id = "speedforge-prod-499002"
        secret_id  = "oci-runner-kubeconfig"
      }
    }
    node_pools = {
      linux_spot = {
        machine_class = "flex-4c-16g"
        capacity_type = "spot"
        min_size      = 0
        max_size      = 10
        labels = {
          "selamy.dev/runner-pool" = "linux-spot"
          "selamy.dev/runs-on"     = "linux"
        }
        runner_labels = ["linux", "speedforge"]
      }
    }
  }

  assert {
    condition     = output.cluster_contract.provider_id == "oci-oke"
    error_message = "provider_id must be carried into the cluster contract."
  }

  assert {
    condition     = contains(output.runner_labels, "linux") && contains(output.runner_labels, "linux_spot")
    error_message = "runner labels must include explicit labels plus the pool name."
  }

  assert {
    condition     = output.node_selector_labels.linux_spot["selamy.dev/runner-pool"] == "linux-spot"
    error_message = "node selector labels must be preserved for platform consumers."
  }
}
