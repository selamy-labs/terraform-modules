mock_provider "helm" {}

variables {
  name                 = "speedforge-large"
  chart_version        = "0.12.1"
  github_config_url    = "https://github.com/selamy-labs"
  github_config_secret = "github-runner-auth"
  min_runners          = 0
  max_runners          = 8
  runner_image         = "ghcr.io/selamy-labs/runner:v1"
}

run "scale_to_zero_and_custom_image" {
  command = plan

  assert {
    condition     = strcontains(local.values_yaml, "\"minRunners\": 0")
    error_message = "minRunners should allow scale-to-zero."
  }

  assert {
    condition     = strcontains(local.values_yaml, "\"maxRunners\": 8")
    error_message = "maxRunners not propagated."
  }

  assert {
    condition     = strcontains(local.values_yaml, "\"image\": \"ghcr.io/selamy-labs/runner:v1\"")
    error_message = "custom runner image not propagated."
  }
}
