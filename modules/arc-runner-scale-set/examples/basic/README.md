# Basic ARC runner scale set

Deploys a GitHub Actions Runner Controller (ARC) runner scale set against the
`selamy-labs` org with scale-to-zero, using the upstream
`gha-runner-scale-set` chart through the canonical module.

```bash
tofu init
tofu plan
```

Requires:
- An ARC controller already installed (`gha-runner-scale-set-controller`).
- The `github-runner-auth` Secret present in the target namespace.

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_agents_runners"></a> [agents\_runners](#module\_agents\_runners) | ../../ | n/a |

## Resources

No resources.

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_release_name"></a> [release\_name](#output\_release\_name) | n/a |
<!-- END_TF_DOCS -->
