mock_provider "google" {}

variables {
  project_id       = "test-project-123456"
  secret_id        = "test-secret"
  secret_data      = "supersecret"
  accessor_members = ["serviceAccount:test@test-project-123456.iam.gserviceaccount.com"]
  labels           = { env = "test" }
}

run "creates_secret" {
  command = plan

  assert {
    condition     = google_secret_manager_secret.this.secret_id == "test-secret"
    error_message = "Secret ID mismatch."
  }

  assert {
    condition     = google_secret_manager_secret.this.project == "test-project-123456"
    error_message = "Project mismatch."
  }
}

run "creates_version_when_data_provided" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_version.this) == 1
    error_message = "Expected one secret version."
  }
}

run "creates_iam_binding" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_iam_member.accessors) == 1
    error_message = "Expected one IAM binding."
  }
}
