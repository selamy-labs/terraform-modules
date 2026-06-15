mock_provider "google" {}

override_resource {
  target = google_service_account.this
  values = {
    name  = "projects/test-project-123456/serviceAccounts/test-sa-account@test-project-123456.iam.gserviceaccount.com"
    email = "test-sa-account@test-project-123456.iam.gserviceaccount.com"
  }
}

variables {
  project_id              = "test-project-123456"
  account_id              = "test-sa-account"
  display_name            = "Test SA"
  wif_k8s_namespace       = "default"
  wif_k8s_service_account = "my-app"
  project_roles           = ["roles/logging.logWriter"]
}

run "creates_service_account" {
  command = plan

  assert {
    condition     = google_service_account.this.account_id == "test-sa-account"
    error_message = "SA account_id mismatch."
  }

  assert {
    condition     = google_service_account.this.project == "test-project-123456"
    error_message = "SA project mismatch."
  }
}

run "creates_wif_binding" {
  command = plan

  assert {
    condition     = length(google_service_account_iam_member.workload_identity) > 0
    error_message = "Expected WIF IAM binding."
  }
}

run "creates_project_role" {
  command = plan

  assert {
    condition     = length(google_project_iam_member.roles) == 1
    error_message = "Expected one project IAM role binding."
  }
}
