module "example_repo" {
  source = "../../"

  name        = "my-example-repo"
  description = "An example repository managed by OpenTofu."
  visibility  = "private"

  topics = ["opentofu", "example"]

  branch_protection_enabled = true
  required_status_checks    = ["ci / lint"]
  allow_auto_merge          = true
}

output "repo_url" {
  value = module.example_repo.html_url
}
