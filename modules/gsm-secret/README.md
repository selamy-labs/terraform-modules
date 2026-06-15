# gsm-secret

Creates a Google Secret Manager secret with optional version and IAM accessor bindings.

## Usage

```hcl
module "my_secret" {
  source = "github.com/selamy-labs/terraform-modules//modules/gsm-secret"

  project_id = "my-project"
  secret_id  = "my-secret"

  secret_data      = "s3cret"
  accessor_members = ["serviceAccount:app@my-project.iam.gserviceaccount.com"]
}
```

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
