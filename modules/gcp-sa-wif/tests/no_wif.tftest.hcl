mock_provider "google" {}

variables {
  project_id   = "test-project-123456"
  account_id   = "test-sa-plain"
  display_name = "Plain SA"
}

run "no_wif_bindings_when_not_configured" {
  command = plan

  assert {
    condition     = length(google_service_account_iam_member.workload_identity) == 0
    error_message = "Expected no WIF bindings when wif vars are null."
  }
}

run "no_project_roles_when_empty" {
  command = plan

  assert {
    condition     = length(google_project_iam_member.roles) == 0
    error_message = "Expected no project role bindings when empty."
  }
}
