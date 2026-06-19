# gsm-secret

Creates a Google Secret Manager secret with optional version and IAM accessor bindings.

## Usage

```hcl
module "my_secret" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/gsm-secret?ref=v0.2.0"

  project_id = "my-project"
  secret_id  = "my-secret"

  secret_data      = "s3cret"
  accessor_members = ["serviceAccount:app@my-project.iam.gserviceaccount.com"]

  # Use stable keys when migrating existing singleton IAM resources.
  named_accessor_members = {
    external_secrets = "serviceAccount:eso@my-project.iam.gserviceaccount.com"
  }
  version_adder_members = {
    operator = "user:operator@example.com"
  }
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_google"></a> [google](#requirement\_google) | >= 5.0, < 7.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | >= 5.0, < 7.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_secret_manager_secret.this](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret) | resource |
| [google_secret_manager_secret_iam_member.accessors](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret_iam_member) | resource |
| [google_secret_manager_secret_iam_member.version_adders](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret_iam_member) | resource |
| [google_secret_manager_secret_version.this](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret_version) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_secret_id"></a> [secret\_id](#input\_secret\_id) | The secret ID within Secret Manager. | `string` | n/a | yes |
| <a name="input_accessor_members"></a> [accessor\_members](#input\_accessor\_members) | List of IAM members granted secretmanager.secretAccessor (e.g. serviceAccount:x@proj.iam.gserviceaccount.com). | `list(string)` | `[]` | no |
| <a name="input_labels"></a> [labels](#input\_labels) | Labels to attach to the secret. | `map(string)` | `{}` | no |
| <a name="input_named_accessor_members"></a> [named\_accessor\_members](#input\_named\_accessor\_members) | Map of stable IAM member keys to members granted secretmanager.secretAccessor. Use when migrating existing singleton IAM resources without changing Terraform addresses. | `map(string)` | `{}` | no |
| <a name="input_secret_data"></a> [secret\_data](#input\_secret\_data) | Optional secret payload. When null, only the secret resource is created (no version). | `string` | `null` | no |
| <a name="input_version_adder_members"></a> [version\_adder\_members](#input\_version\_adder\_members) | Map of stable IAM member keys to members granted secretmanager.secretVersionAdder. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_secret_id"></a> [secret\_id](#output\_secret\_id) | The fully-qualified secret ID. |
| <a name="output_secret_name"></a> [secret\_name](#output\_secret\_name) | The secret resource name (projects/*/secrets/*). |
| <a name="output_version_id"></a> [version\_id](#output\_version\_id) | The secret version ID, if a version was created. |
<!-- END_TF_DOCS -->
