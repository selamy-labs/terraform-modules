module "example_secret" {
  source = "../../"

  project_id = "my-gcp-project"
  secret_id  = "my-app-secret"

  secret_data = "s3cret-value"

  accessor_members = [
    "serviceAccount:my-app@my-gcp-project.iam.gserviceaccount.com",
  ]

  labels = {
    environment = "dev"
    managed_by  = "opentofu"
  }
}

output "secret_id" {
  value = module.example_secret.secret_id
}
