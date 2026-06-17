locals {
  # Typed values-contract for the upstream gha-runner-scale-set chart. This is
  # the single canonical shape so orgs stop home-rolling runner-scale-set charts
  # (e.g. matchpoint-github-runners-helm) or wrapping TF (spot-argocd-cloudspace).
  base_values = {
    githubConfigUrl    = var.github_config_url
    githubConfigSecret = var.github_config_secret
    runnerGroup        = var.runner_group
    minRunners         = var.min_runners
    maxRunners         = var.max_runners

    controllerServiceAccount = {
      namespace = var.controller_service_account_namespace
      name      = var.controller_service_account_name
    }

    template = {
      spec = {
        containers = [{
          name      = "runner"
          image     = var.runner_image
          command   = ["/home/runner/run.sh"]
          resources = var.runner_resources
        }]
      }
    }
  }

  values_yaml = yamlencode(local.base_values)
}
