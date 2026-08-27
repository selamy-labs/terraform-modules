# Complete example

This example shows a directory-defined agent with a skill, workspace source,
typed output, evaluation cases, a tool-scoped remote MCP server, and a default
deny network allowlist.

The header credential is an immutable Secret Manager version reference. The
reconciler resolves its value only while calling the API; the value never enters
the module input, output, or state.

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
| <a name="output_active_agents"></a> [active\_agents](#output\_active\_agents) | n/a |
| <a name="output_drift_report"></a> [drift\_report](#output\_drift\_report) | n/a |
<!-- END_TF_DOCS -->