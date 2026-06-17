module "agents_runners" {
  source = "../../"

  name          = "agents-gke"
  namespace     = "github-runners"
  chart_version = "0.12.1"

  github_config_url    = "https://github.com/selamy-labs"
  github_config_secret = "github-runner-auth"

  min_runners = 0
  max_runners = 2
}

output "release_name" {
  value = module.agents_runners.release_name
}
