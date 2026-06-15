mock_provider "google" {}

variables {
  project_id  = "test-project-123456"
  secret_id   = "test-secret-no-data"
  secret_data = null
}

run "skips_version_when_no_data" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_version.this) == 0
    error_message = "Expected no secret version when secret_data is null."
  }
}

run "skips_iam_when_empty" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_iam_member.accessors) == 0
    error_message = "Expected no IAM bindings when accessor_members is empty."
  }
}
