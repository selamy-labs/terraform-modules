# OCI OKE Module

Creates a small Oracle Kubernetes Engine substrate for runner experiments:

- one VCN with public API/LB subnets and private node/pod subnets
- a BASIC OKE cluster
- one preemptible node pool for normal CI runner capacity
- one optional on-demand fallback pool for scheduler/autoscaler escape capacity

The module intentionally does not configure the OCI provider. Callers should
prefer workload identity where available, or inject the OCI API key through the
existing secret manager path.

## Example

```hcl
module "oke" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/oci-oke?ref=<pinned-ref>"

  compartment_id     = var.oci_compartment_id
  name               = "speedforge-oke-runners-exp"
  kubernetes_version = "v1.31.1"

  availability_domain = var.oci_availability_domain
  node_image_id       = var.oci_oke_node_image_id

  preemptible_node_shape = "VM.Standard.E4.Flex"
  preemptible_ocpus      = 2
  preemptible_memory_gb  = 16
  preemptible_node_count = 1

  fallback_node_shape = "VM.Standard.E4.Flex"
  fallback_ocpus      = 2
  fallback_memory_gb  = 16
  fallback_node_count = 1
}
```

Keep `preemptible_node_count` and `fallback_node_count` at least `1` for the
side-by-side experiment so ARC has real baseline capacity on both pools and the
fallback pool is proven usable before any workload is moved.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_oci"></a> [oci](#requirement\_oci) | >= 6.0, < 8.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_oci"></a> [oci](#provider\_oci) | >= 6.0, < 8.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [oci_containerengine_cluster.this](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/containerengine_cluster) | resource |
| [oci_containerengine_node_pool.fallback](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/containerengine_node_pool) | resource |
| [oci_containerengine_node_pool.preemptible](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/containerengine_node_pool) | resource |
| [oci_core_internet_gateway.this](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_internet_gateway) | resource |
| [oci_core_nat_gateway.this](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_nat_gateway) | resource |
| [oci_core_route_table.private](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_route_table) | resource |
| [oci_core_route_table.public](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_route_table) | resource |
| [oci_core_security_list.private](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_security_list) | resource |
| [oci_core_security_list.public](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_security_list) | resource |
| [oci_core_service_gateway.this](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_service_gateway) | resource |
| [oci_core_subnet.api](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_subnet) | resource |
| [oci_core_subnet.lb](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_subnet) | resource |
| [oci_core_subnet.nodes](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_subnet) | resource |
| [oci_core_subnet.pods](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_subnet) | resource |
| [oci_core_vcn.this](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_vcn) | resource |
| [oci_core_services.all](https://registry.terraform.io/providers/oracle/oci/latest/docs/data-sources/core_services) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_availability_domain"></a> [availability\_domain](#input\_availability\_domain) | OCI availability domain name used for the initial side-by-side experiment node pools. | `string` | n/a | yes |
| <a name="input_compartment_id"></a> [compartment\_id](#input\_compartment\_id) | OCI compartment OCID for all OKE experiment resources. | `string` | n/a | yes |
| <a name="input_kubernetes_version"></a> [kubernetes\_version](#input\_kubernetes\_version) | OKE Kubernetes version, for example v1.31.1. | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Short resource prefix for the OKE experiment. | `string` | n/a | yes |
| <a name="input_node_image_id"></a> [node\_image\_id](#input\_node\_image\_id) | OKE worker node image OCID. Keep explicit so applies are reproducible. | `string` | n/a | yes |
| <a name="input_api_subnet_cidr"></a> [api\_subnet\_cidr](#input\_api\_subnet\_cidr) | Public subnet for the Kubernetes API endpoint. | `string` | `"10.80.0.0/24"` | no |
| <a name="input_boot_volume_size_gb"></a> [boot\_volume\_size\_gb](#input\_boot\_volume\_size\_gb) | Boot volume size for worker nodes. | `number` | `100` | no |
| <a name="input_enable_fallback_pool"></a> [enable\_fallback\_pool](#input\_enable\_fallback\_pool) | Create the on-demand fallback node pool. | `bool` | `true` | no |
| <a name="input_endpoint_allowed_cidrs"></a> [endpoint\_allowed\_cidrs](#input\_endpoint\_allowed\_cidrs) | CIDRs allowed to reach the public Kubernetes API endpoint. | `list(string)` | <pre>[<br/>  "0.0.0.0/0"<br/>]</pre> | no |
| <a name="input_fallback_memory_gb"></a> [fallback\_memory\_gb](#input\_fallback\_memory\_gb) | Memory for each fallback flex node. | `number` | `16` | no |
| <a name="input_fallback_node_count"></a> [fallback\_node\_count](#input\_fallback\_node\_count) | Initial on-demand fallback node count. Use min>=1 so fallback capacity is tested. | `number` | `1` | no |
| <a name="input_fallback_node_shape"></a> [fallback\_node\_shape](#input\_fallback\_node\_shape) | OCI compute shape for on-demand fallback runner nodes. | `string` | `"VM.Standard.E4.Flex"` | no |
| <a name="input_fallback_ocpus"></a> [fallback\_ocpus](#input\_fallback\_ocpus) | OCPUs for each fallback flex node. | `number` | `2` | no |
| <a name="input_freeform_tags"></a> [freeform\_tags](#input\_freeform\_tags) | Freeform tags applied to OCI resources. | `map(string)` | `{}` | no |
| <a name="input_lb_subnet_cidr"></a> [lb\_subnet\_cidr](#input\_lb\_subnet\_cidr) | Public subnet for Kubernetes load balancers. | `string` | `"10.80.1.0/24"` | no |
| <a name="input_node_subnet_cidr"></a> [node\_subnet\_cidr](#input\_node\_subnet\_cidr) | Private subnet for OKE worker nodes. | `string` | `"10.80.10.0/24"` | no |
| <a name="input_pod_subnet_cidr"></a> [pod\_subnet\_cidr](#input\_pod\_subnet\_cidr) | Private subnet used by OCI VCN-native pod networking. | `string` | `"10.80.20.0/22"` | no |
| <a name="input_pods_cidr"></a> [pods\_cidr](#input\_pods\_cidr) | Kubernetes pods CIDR used by the OKE cluster record. | `string` | `"10.244.0.0/16"` | no |
| <a name="input_preemptible_memory_gb"></a> [preemptible\_memory\_gb](#input\_preemptible\_memory\_gb) | Memory for each preemptible flex node. | `number` | `16` | no |
| <a name="input_preemptible_node_count"></a> [preemptible\_node\_count](#input\_preemptible\_node\_count) | Initial preemptible node count. Use min>=1 for the side-by-side runner experiment. | `number` | `1` | no |
| <a name="input_preemptible_node_shape"></a> [preemptible\_node\_shape](#input\_preemptible\_node\_shape) | OCI compute shape for preemptible runner nodes. | `string` | `"VM.Standard.E4.Flex"` | no |
| <a name="input_preemptible_ocpus"></a> [preemptible\_ocpus](#input\_preemptible\_ocpus) | OCPUs for each preemptible flex node. | `number` | `2` | no |
| <a name="input_public_endpoint_enabled"></a> [public\_endpoint\_enabled](#input\_public\_endpoint\_enabled) | Expose the Kubernetes API endpoint publicly for the experiment. Restrict with endpoint\_allowed\_cidrs. | `bool` | `true` | no |
| <a name="input_service_cidr"></a> [service\_cidr](#input\_service\_cidr) | Kubernetes service CIDR. | `string` | `"10.96.0.0/16"` | no |
| <a name="input_vcn_cidr"></a> [vcn\_cidr](#input\_vcn\_cidr) | VCN CIDR block. | `string` | `"10.80.0.0/16"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_subnet_id"></a> [api\_subnet\_id](#output\_api\_subnet\_id) | Kubernetes API endpoint subnet OCID. |
| <a name="output_cluster_id"></a> [cluster\_id](#output\_cluster\_id) | OKE cluster OCID. |
| <a name="output_cluster_name"></a> [cluster\_name](#output\_cluster\_name) | OKE cluster name. |
| <a name="output_fallback_node_pool_id"></a> [fallback\_node\_pool\_id](#output\_fallback\_node\_pool\_id) | Fallback on-demand node pool OCID, when enabled. |
| <a name="output_node_subnet_id"></a> [node\_subnet\_id](#output\_node\_subnet\_id) | Worker node subnet OCID. |
| <a name="output_pod_subnet_id"></a> [pod\_subnet\_id](#output\_pod\_subnet\_id) | Pod subnet OCID. |
| <a name="output_preemptible_node_pool_id"></a> [preemptible\_node\_pool\_id](#output\_preemptible\_node\_pool\_id) | Preemptible node pool OCID. |
| <a name="output_vcn_id"></a> [vcn\_id](#output\_vcn\_id) | VCN OCID. |
<!-- END_TF_DOCS -->
