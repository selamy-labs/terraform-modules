mock_provider "helm" {}

variables {
  name                 = "agents-gke"
  namespace            = "github-runners"
  chart_version        = "0.12.1"
  github_config_url    = "https://github.com/selamy-labs"
  github_config_secret = "github-runner-auth"
  min_runners          = 0
  max_runners          = 2
}

run "creates_release_with_name" {
  command = plan

  assert {
    condition     = helm_release.this.name == "agents-gke"
    error_message = "Release name mismatch."
  }

  assert {
    condition     = helm_release.this.chart == "gha-runner-scale-set"
    error_message = "Should deploy the upstream gha-runner-scale-set chart."
  }

  assert {
    condition     = helm_release.this.version == "0.12.1"
    error_message = "Chart version not pinned through."
  }

  assert {
    condition     = helm_release.this.namespace == "github-runners"
    error_message = "Namespace mismatch."
  }
}

run "values_carry_canonical_contract" {
  command = plan

  assert {
    condition     = strcontains(local.values_yaml, "\"githubConfigUrl\": \"https://github.com/selamy-labs\"")
    error_message = "githubConfigUrl missing from rendered values."
  }

  assert {
    condition     = strcontains(local.values_yaml, "\"githubConfigSecret\": \"github-runner-auth\"")
    error_message = "githubConfigSecret missing from rendered values."
  }

  assert {
    condition     = strcontains(local.values_yaml, "\"maxRunners\": 2")
    error_message = "maxRunners missing from rendered values."
  }

  assert {
    condition     = strcontains(local.values_yaml, "\"name\": \"arc-gha-rs-controller\"")
    error_message = "controller service account default missing."
  }
}
