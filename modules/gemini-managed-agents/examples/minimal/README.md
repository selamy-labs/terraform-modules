# Minimal example

This example declares one network-isolated document-review agent with one
immutable revision. OAuth is the default authentication mode.

The revision directory is portable: runtime files are mounted into the managed
sandbox, while the output schema is returned to the caller for typed
interaction validation.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.0, < 2.0.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_managed_agents"></a> [managed\_agents](#module\_managed\_agents) | git::https://github.com/selamy-labs/terraform-modules.git//modules/gemini-managed-agents | v0.9.0 |

## Resources

No resources.

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_active_agent"></a> [active\_agent](#output\_active\_agent) | n/a |
<!-- END_TF_DOCS -->