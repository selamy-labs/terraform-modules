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
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_google"></a> [google](#requirement\_google) | ~> 5.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | ~> 5.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_project_iam_member.roles](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_service_account.this](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_service_account_iam_member.workload_identity](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The service account ID (the part before @). | `string` | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_additional_wif_members"></a> [additional\_wif\_members](#input\_additional\_wif\_members) | Extra IAM members to grant workloadIdentityUser on this SA. | `list(string)` | `[]` | no |
| <a name="input_description"></a> [description](#input\_description) | Description of the service account. | `string` | `""` | no |
| <a name="input_display_name"></a> [display\_name](#input\_display\_name) | Human-readable display name for the service account. | `string` | `""` | no |
| <a name="input_project_roles"></a> [project\_roles](#input\_project\_roles) | List of IAM roles to grant to this SA at the project level. | `list(string)` | `[]` | no |
| <a name="input_wif_k8s_namespace"></a> [wif\_k8s\_namespace](#input\_wif\_k8s\_namespace) | Kubernetes namespace for WIF binding. | `string` | `null` | no |
| <a name="input_wif_k8s_service_account"></a> [wif\_k8s\_service\_account](#input\_wif\_k8s\_service\_account) | Kubernetes service account name for WIF binding. | `string` | `null` | no |
| <a name="input_wif_pool_provider"></a> [wif\_pool\_provider](#input\_wif\_pool\_provider) | Full resource name of the Workload Identity pool provider (projects/NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER). | `string` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_email"></a> [email](#output\_email) | The service account email. |
| <a name="output_member"></a> [member](#output\_member) | The IAM member string for this service account. |
| <a name="output_name"></a> [name](#output\_name) | The fully-qualified service account resource name. |
| <a name="output_unique_id"></a> [unique\_id](#output\_unique\_id) | The unique numeric ID of the service account. |
<!-- END_TF_DOCS -->
