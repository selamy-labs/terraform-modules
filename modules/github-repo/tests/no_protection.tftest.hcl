mock_provider "github" {}

variables {
  name                      = "test-repo-open"
  branch_protection_enabled = false
}

run "no_branch_protection_when_disabled" {
  command = plan

  assert {
    condition     = length(github_branch_protection.default) == 0
    error_message = "Expected no branch protection."
  }
}

run "defaults_are_sensible" {
  command = plan

  assert {
    condition     = github_repository.this.allow_auto_merge == true
    error_message = "Expected auto_merge default true."
  }

  assert {
    condition     = github_repository.this.delete_branch_on_merge == true
    error_message = "Expected delete_branch_on_merge default true."
  }
}
