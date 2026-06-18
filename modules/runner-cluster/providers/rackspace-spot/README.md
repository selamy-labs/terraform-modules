# runner-cluster/providers/rackspace-spot

Rackspace Spot adapter for the provider-portable `runner-cluster` contract.

Provider-native Rackspace Spot cluster, node pool, networking, and autoscaler
resources belong in this adapter. The provider-neutral platform layer must
consume only the exported `cluster_contract`, `kubeconfig`, `node_pools`,
`runner_labels`, and `node_selector_labels` outputs.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_contract"></a> [contract](#module\_contract) | ../.. | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_kubeconfig"></a> [kubeconfig](#input\_kubeconfig) | Reference to the Rackspace Spot kubeconfig. Contains references only, not secret values. | <pre>object({<br/>    source  = string<br/>    context = optional(string)<br/>    path    = optional(string)<br/>    secret_ref = optional(object({<br/>      project_id = string<br/>      secret_id  = string<br/>      version    = optional(string, "latest")<br/>      key        = optional(string)<br/>    }))<br/>  })</pre> | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Logical runner cluster name. | `string` | n/a | yes |
| <a name="input_node_pools"></a> [node\_pools](#input\_node\_pools) | Rackspace Spot node pools normalized to the runner-cluster contract. | <pre>map(object({<br/>    machine_class = string<br/>    capacity_type = string<br/>    min_size      = number<br/>    max_size      = number<br/>    desired_size  = optional(number)<br/>    labels        = map(string)<br/>    taints = optional(list(object({<br/>      key    = string<br/>      value  = optional(string)<br/>      effect = string<br/>    })), [])<br/>    runner_labels = optional(list(string), [])<br/>    pool_id       = optional(string)<br/>    region        = optional(string)<br/>  }))</pre> | n/a | yes |
| <a name="input_metadata"></a> [metadata](#input\_metadata) | Free-form metadata for ADR links, rollout notes, and ownership. | `map(string)` | `{}` | no |
| <a name="input_platform"></a> [platform](#input\_platform) | Provider-neutral platform defaults layered onto the cluster by the consumer. | <pre>object({<br/>    arc_namespace       = optional(string, "arc-runners")<br/>    argocd_namespace    = optional(string, "argocd")<br/>    tenant_registry_ref = optional(string)<br/>  })</pre> | `{}` | no |
| <a name="input_runner_labels"></a> [runner\_labels](#input\_runner\_labels) | Global GitHub Actions runs-on labels exposed by this cluster. | `list(string)` | `[]` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cluster_contract"></a> [cluster\_contract](#output\_cluster\_contract) | Provider-neutral runner-cluster contract. |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | Kubeconfig reference for provider-neutral Kubernetes providers. |
| <a name="output_node_pools"></a> [node\_pools](#output\_node\_pools) | Normalized node pools. |
| <a name="output_node_selector_labels"></a> [node\_selector\_labels](#output\_node\_selector\_labels) | Node selector labels keyed by node pool name. |
| <a name="output_runner_labels"></a> [runner\_labels](#output\_runner\_labels) | Distinct GitHub Actions runs-on labels exposed by this cluster. |
<!-- END_TF_DOCS -->