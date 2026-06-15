# github-repo

Creates a GitHub repository with default settings and optional branch protection. Designed to declaratively manage repositories like terraform-modules and helm-charts.

## Usage

```hcl
module "my_repo" {
  source = "github.com/selamy-labs/terraform-modules//modules/github-repo"

  name        = "my-repo"
  description = "Managed by OpenTofu"
  visibility  = "private"

  branch_protection_enabled = true
  required_status_checks    = ["ci / lint"]
}
```

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
