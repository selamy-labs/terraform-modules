module "example_sa" {
  source = "../../"

  project_id   = "my-gcp-project"
  account_id   = "my-app-sa"
  display_name = "My App Service Account"

  wif_k8s_namespace       = "default"
  wif_k8s_service_account = "my-app"

  project_roles = [
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
  ]
}

output "sa_email" {
  value = module.example_sa.email
}
