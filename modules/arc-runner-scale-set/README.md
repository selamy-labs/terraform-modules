# arc-runner-scale-set

Canonical module for a GitHub Actions Runner Controller (ARC) **runner scale set**. Wraps the upstream `gha-runner-scale-set` Helm chart (`oci://ghcr.io/actions/actions-runner-controller-charts`) behind a typed, pinned values-contract so orgs stop home-rolling runner-scale-set charts or wrapping Terraform.

This module deploys ONLY a runner scale set. The ARC controller (`gha-runner-scale-set-controller`) is a separate, cluster-singleton install and is out of scope here.

> Scale-set names must be unique per controller installation — a given runner label cannot run in two scale sets at once (active-passive failover, not active-active).

## Usage

```hcl
module "agents_runners" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/arc-runner-scale-set?ref=v0.3.0"

  name          = "agents-gke"
  namespace     = "github-runners"
  chart_version = "0.12.1"

  github_config_url    = "https://github.com/selamy-labs"
  github_config_secret = "github-runner-auth"

  min_runners = 0
  max_runners = 2
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | >= 2.12, < 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_helm"></a> [helm](#provider\_helm) | >= 2.12, < 3.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [helm_release.this](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_chart_version"></a> [chart\_version](#input\_chart\_version) | Version of the upstream gha-runner-scale-set chart (pin explicitly; must match the installed controller). | `string` | n/a | yes |
| <a name="input_github_config_secret"></a> [github\_config\_secret](#input\_github\_config\_secret) | Name of the pre-existing Kubernetes Secret holding GitHub App / PAT auth for ARC (created out-of-band, e.g. via ExternalSecrets). | `string` | n/a | yes |
| <a name="input_github_config_url"></a> [github\_config\_url](#input\_github\_config\_url) | GitHub org or repo URL the runners attach to (e.g. https://github.com/selamy-labs). | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Release name and runner scale-set name. Must be unique per ARC controller installation (a label cannot run in two scale sets at once). | `string` | n/a | yes |
| <a name="input_controller_service_account_name"></a> [controller\_service\_account\_name](#input\_controller\_service\_account\_name) | Name of the ARC controller ServiceAccount. | `string` | `"arc-gha-rs-controller"` | no |
| <a name="input_controller_service_account_namespace"></a> [controller\_service\_account\_namespace](#input\_controller\_service\_account\_namespace) | Namespace of the ARC controller ServiceAccount. | `string` | `"arc-systems"` | no |
| <a name="input_create_namespace"></a> [create\_namespace](#input\_create\_namespace) | Whether the helm\_release should create the namespace. | `bool` | `true` | no |
| <a name="input_extra_values"></a> [extra\_values](#input\_extra\_values) | Additional raw Helm values (YAML string) merged last, for escape-hatch overrides. Keep empty in the common case. | `string` | `""` | no |
| <a name="input_max_runners"></a> [max\_runners](#input\_max\_runners) | Maximum concurrent runners. | `number` | `2` | no |
| <a name="input_min_runners"></a> [min\_runners](#input\_min\_runners) | Minimum idle runners (0 = scale-to-zero). | `number` | `0` | no |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | Kubernetes namespace for the runner scale set. | `string` | `"github-runners"` | no |
| <a name="input_runner_group"></a> [runner\_group](#input\_runner\_group) | GitHub runner group the scale set joins. | `string` | `"Default"` | no |
| <a name="input_runner_image"></a> [runner\_image](#input\_runner\_image) | Runner container image. | `string` | `"ghcr.io/actions/actions-runner:latest"` | no |
| <a name="input_runner_resources"></a> [runner\_resources](#input\_runner\_resources) | Runner container resource requests/limits. | <pre>object({<br/>    requests = optional(map(string), { cpu = "250m", memory = "512Mi" })<br/>    limits   = optional(map(string), { cpu = "1", memory = "2Gi" })<br/>  })</pre> | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_chart_version"></a> [chart\_version](#output\_chart\_version) | The deployed gha-runner-scale-set chart version. |
| <a name="output_namespace"></a> [namespace](#output\_namespace) | Namespace the runner scale set is deployed into. |
| <a name="output_release_name"></a> [release\_name](#output\_release\_name) | The Helm release name (== the runner scale-set name / GitHub runner label). |
| <a name="output_status"></a> [status](#output\_status) | Status of the Helm release. |
<!-- END_TF_DOCS -->
