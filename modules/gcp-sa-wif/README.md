# gcp-sa-wif

Creates a GCP service account with Workload Identity Federation bindings and optional project-level IAM roles.

## Usage

```hcl
module "my_sa" {
  source = "github.com/selamy-labs/terraform-modules//modules/gcp-sa-wif"

  project_id              = "my-project"
  account_id              = "my-app-sa"
  wif_k8s_namespace       = "default"
  wif_k8s_service_account = "my-app"

  project_roles = ["roles/secretmanager.secretAccessor"]
}
```

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
