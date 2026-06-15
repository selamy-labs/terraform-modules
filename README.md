# terraform-modules

Reusable OpenTofu modules for cloud/provider resources. Layer split: TF = cloud, Helm = k8s.

## Modules

| Module | Description |
|--------|-------------|
| [gsm-secret](modules/gsm-secret/) | Google Secret Manager secret + optional version + IAM |
| [gcp-sa-wif](modules/gcp-sa-wif/) | GCP service account + Workload Identity Federation |
| [github-repo](modules/github-repo/) | GitHub repository + branch protection + defaults |
| [monitoring-policy](modules/monitoring-policy/) | Google Cloud Monitoring alert policy scoped by label |

## Usage

```hcl
module "my_secret" {
  source = "github.com/selamy-labs/terraform-modules//modules/gsm-secret"
  # ...
}
```

## CI

- **tflint** - Terraform linting with Google ruleset
- **trivy** - Security misconfiguration scanning
- **tofu test** - Module tests using mock providers
- **terraform-docs** - README drift check
- **tofu validate** - Syntax and configuration validation
