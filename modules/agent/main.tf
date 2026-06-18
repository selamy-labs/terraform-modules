resource "google_secret_manager_secret" "credentials" {
  for_each = local.creatable_credentials

  project   = var.project_id
  secret_id = local.credential_secret_ids[each.key]

  replication {
    auto {}
  }

  labels = merge(local.common_labels, each.value.labels)
}

resource "google_secret_manager_secret_iam_member" "credential_accessors" {
  for_each = local.credential_accessor_bindings

  project   = var.project_id
  secret_id = google_secret_manager_secret.credentials[each.value.credential_name].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value.member
}
