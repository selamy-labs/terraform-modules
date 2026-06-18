# terraform-modules

Reusable OpenTofu modules for cloud/provider resources. Layer split: TF = cloud, Helm = k8s.

## Modules

| Module | Description |
|--------|-------------|
| [agent](modules/agent/) | Canonical Selamy agent/employee contract + GSM credential shells |
| [gsm-secret](modules/gsm-secret/) | Google Secret Manager secret + optional version + IAM |
| [gcp-sa-wif](modules/gcp-sa-wif/) | GCP service account + Workload Identity Federation |
| [github-repo](modules/github-repo/) | GitHub repository + branch protection + defaults |
| [monitoring-policy](modules/monitoring-policy/) | Google Cloud Monitoring alert policy scoped by label |

> **New repos: ingest canonical IaC by default.** Never home-roll a module
> that duplicates one of these — see [NEW_REPO_BOOTSTRAP.md](NEW_REPO_BOOTSTRAP.md).

## Usage

Consume modules by **git source pinned to a semver tag** (`?ref=vX.Y.Z`). Never
reference an unpinned `main` and never copy a module into a consumer repo.

```hcl
module "my_secret" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/gsm-secret?ref=v0.2.0"

  project_id = "my-project"
  secret_id  = "my-secret"
}
```

## Versioning & adoption

Modules are released as immutable semver git tags. Consumers pin to a tag so an
upstream change can never silently alter a consumer's plan.

**Adoption recipe** (replace an inlined resource block with a pinned module):

1. Find the equivalent module in [`modules/`](modules/).
2. Replace the inline `resource` block(s) with a `module` block whose `source`
   is `git::https://github.com/selamy-labs/terraform-modules.git//modules/<name>?ref=v<tag>`.
3. Map the resource arguments onto the module's variables (see the module README).
4. Run `tofu init && tofu plan` and confirm the plan is a no-op (or only the
   intended changes) before applying — `moved` blocks can preserve state.
5. To pick up a new module release, bump the `?ref=` tag and re-plan.

To cut a new release: merge to `main`, then push a new `vX.Y.Z` tag
(MAJOR = breaking variable/output change, MINOR = new module/variable,
PATCH = fix). Pre-`v1.0.0` minors may include breaking changes.

## CI

- **tflint** - Terraform linting with Google ruleset
- **trivy** - Security misconfiguration scanning
- **tofu test** - Module tests using mock providers
- **terraform-docs** - README drift check
- **tofu validate** - Syntax and configuration validation
