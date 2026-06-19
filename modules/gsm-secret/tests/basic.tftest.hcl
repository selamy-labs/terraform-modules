mock_provider "google" {}

variables {
  project_id             = "test-project-123456"
  secret_id              = "test-secret"
  secret_data            = "supersecret"
  accessor_members       = ["serviceAccount:test@test-project-123456.iam.gserviceaccount.com"]
  named_accessor_members = { eso = "serviceAccount:eso@test-project-123456.iam.gserviceaccount.com" }
  version_adder_members  = { patrick = "user:patrick@example.com" }
  labels                 = { env = "test" }
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
    condition     = length(google_secret_manager_secret_iam_member.accessors) == 2
    error_message = "Expected two accessor IAM bindings."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.accessors["eso"].member == "serviceAccount:eso@test-project-123456.iam.gserviceaccount.com"
    error_message = "Expected named accessor binding to use stable key."
  }
}

run "creates_version_adder_binding" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_iam_member.version_adders) == 1
    error_message = "Expected one version adder IAM binding."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.version_adders["patrick"].role == "roles/secretmanager.secretVersionAdder"
    error_message = "Expected version adder role."
  }
}
