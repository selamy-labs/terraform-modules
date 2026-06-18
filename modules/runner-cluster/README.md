# runner-cluster

Provider-portable contract for GitHub Actions runner Kubernetes clusters.

This module is the boundary between:

- **Provider-specific cluster layer:** creates or imports a Kubernetes cluster,
  node pools, networking, and autoscaling for Rackspace Spot, OCI OKE, or GKE.
- **Provider-neutral platform layer:** installs ARC controller, runner scale
  sets, ArgoCD apps, runner config, and tenant registry against a kubeconfig and
  standard node-pool labels.

The module intentionally creates no live resources. It normalizes provider
outputs into one object so platform code can swap providers by changing the
cluster implementation module, not the ARC/ArgoCD layer.

## Example

```hcl
module "runner_cluster" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/runner-cluster?ref=vX.Y.Z"

  name        = "speedforge-runners"
  provider_id = "oci-oke"
  kubeconfig = {
    source = "secret_ref"
    secret_ref = {
      project_id = "speedforge-prod-499002"
      secret_id  = "oci-runner-kubeconfig"
    }
  }

  node_pools = {
    linux_spot = {
      machine_class = "flex-4c-16g"
      capacity_type = "spot"
      min_size      = 0
      max_size      = 20
      labels = {
        "selamy.dev/runner-pool" = "linux-spot"
        "selamy.dev/runs-on"     = "linux"
      }
      runner_labels = ["linux", "speedforge"]
    }
  }
}
```

## Provider Adapters

Provider adapters live under `providers/` and return the same
`cluster_contract` shape:

- `providers/rackspace-spot`
- `providers/oci-oke`
- `providers/gke`

They are the only place provider-native cluster, networking, node pool, and
autoscaler assumptions should live. Shared charts and platform modules consume
only this module's outputs.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |

## Providers

No providers.

## Modules

No modules.

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_kubeconfig"></a> [kubeconfig](#input\_kubeconfig) | Reference to the kubeconfig consumed by the provider-neutral platform layer. This module carries references only, never secret material. | <pre>object({<br/>    source  = string<br/>    context = optional(string)<br/>    path    = optional(string)<br/>    secret_ref = optional(object({<br/>      project_id = string<br/>      secret_id  = string<br/>      version    = optional(string, "latest")<br/>      key        = optional(string)<br/>    }))<br/>  })</pre> | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Logical runner cluster name used by platform consumers. | `string` | n/a | yes |
| <a name="input_node_pools"></a> [node\_pools](#input\_node\_pools) | Provider-normalized node pools. Provider modules map their native pools into this shape. | <pre>map(object({<br/>    machine_class = string<br/>    capacity_type = string<br/>    min_size      = number<br/>    max_size      = number<br/>    desired_size  = optional(number)<br/>    labels        = map(string)<br/>    taints = optional(list(object({<br/>      key    = string<br/>      value  = optional(string)<br/>      effect = string<br/>    })), [])<br/>    runner_labels = optional(list(string), [])<br/>  }))</pre> | n/a | yes |
| <a name="input_provider_id"></a> [provider\_id](#input\_provider\_id) | Cluster implementation behind this contract. | `string` | n/a | yes |
| <a name="input_metadata"></a> [metadata](#input\_metadata) | Free-form metadata for ADR links, rollout notes, and ownership. | `map(string)` | `{}` | no |
| <a name="input_platform"></a> [platform](#input\_platform) | Provider-neutral platform defaults layered onto the cluster by the consumer. | <pre>object({<br/>    arc_namespace       = optional(string, "arc-runners")<br/>    argocd_namespace    = optional(string, "argocd")<br/>    tenant_registry_ref = optional(string)<br/>  })</pre> | `{}` | no |
| <a name="input_runner_labels"></a> [runner\_labels](#input\_runner\_labels) | Global GitHub Actions runs-on labels exposed by this cluster. | `list(string)` | `[]` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cluster_contract"></a> [cluster\_contract](#output\_cluster\_contract) | Provider-neutral runner-cluster contract consumed by ARC, ArgoCD, and tenant registry platform layers. |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | Kubeconfig reference for provider-neutral Kubernetes providers. Contains references only, not secret values. |
| <a name="output_node_pools"></a> [node\_pools](#output\_node\_pools) | Normalized node pools with standard labels and runner capability labels. |
| <a name="output_node_selector_labels"></a> [node\_selector\_labels](#output\_node\_selector\_labels) | Node selector labels keyed by node pool name for runner scale set consumers. |
| <a name="output_runner_labels"></a> [runner\_labels](#output\_runner\_labels) | Distinct GitHub Actions runs-on labels exposed by this cluster. |
<!-- END_TF_DOCS -->