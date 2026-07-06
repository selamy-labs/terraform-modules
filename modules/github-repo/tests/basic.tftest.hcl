mock_provider "github" {}

variables {
  name                      = "test-repo"
  description               = "A test repository"
  visibility                = "private"
  branch_protection_enabled = true
  required_status_checks    = ["ci / lint"]
}

run "creates_repository" {
  command = plan

  assert {
    condition     = github_repository.this.name == "test-repo"
    error_message = "Repo name mismatch."
  }

  assert {
    condition     = github_repository.this.visibility == "private"
    error_message = "Visibility mismatch."
  }

  assert {
    condition     = github_repository.this.allow_squash_merge == true
    error_message = "Expected squash merge enabled."
  }

  assert {
    condition     = github_repository.this.allow_merge_commit == false
    error_message = "Expected merge commits disabled."
  }
}

run "creates_branch_protection" {
  command = plan

  assert {
    condition     = length(github_branch_protection.default) == 1
    error_message = "Expected branch protection."
  }

  assert {
    condition     = github_branch_protection.default[0].required_status_checks[0].strict == true
    error_message = "Expected strict status checks by default."
  }
}

run "allows_non_strict_status_checks" {
  command = plan

  variables {
    strict_status_checks = false
  }

  assert {
    condition     = github_branch_protection.default[0].required_status_checks[0].strict == false
    error_message = "Expected strict status checks override to be honored."
  }
}
