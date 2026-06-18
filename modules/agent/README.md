# agent

Declares the canonical Selamy agent/employee contract. The module keeps the
cloud-side source of truth in OpenTofu: identity, runtime shape, capabilities,
knowledge surfaces, credentials, cron duties, queue ownership, and guardrails.

The module creates Google Secret Manager secret shells and accessor IAM for
declared credentials. Secret values are seeded separately through GSM and synced
to Kubernetes by Helm-rendered ExternalSecrets; this module does not create live
Kubernetes objects.

## Usage

```hcl
module "reid_agent" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/agent?ref=v0.5.0"

  project_id = "patrick-agents-prod"
  agent_name = "reid"

  identity = {
    display_name    = "Reid"
    github_actor    = "reid-max"
    committer_name  = "Reid Max"
    committer_email = "reid@selamy.dev"
    auth_class      = "committer-bot"
  }

  runtime = {
    namespace    = "reid"
    hermes_image = "ghcr.io/selamy-labs/hermes-agent:v1"
    resources = {
      requests = { cpu = "100m", memory = "1536Mi" }
      limits   = { memory = "3Gi" }
    }
    storage = {
      class = "standard-rwo"
      size  = "20Gi"
    }
  }

  capabilities = {
    skills = ["grounded-generation", "verify-real-artifact"]
  }

  credentials = {
    github_token = {
      remote_secret_id  = "reid-gh-token"
      target_secret_name = "reid-credentials"
      accessor_members  = ["serviceAccount:external-secrets@patrick-agents-prod.iam.gserviceaccount.com"]
      keys = [{ secret_key = "GH_TOKEN" }]
    }
  }

  cron = {
    daily_review = {
      schedule = "0 13 * * *"
      command  = "python3 /opt/scripts/reid_daily_review.py"
    }
  }

  lane = {
    queue_name       = "laneq"
    priority_sources = ["finance"]
    issue_repos      = ["selamy-labs/reid"]
  }
}
```

Consumers should feed `agent_contract` and `external_secret_specs` into Helm or
GitOps layers pinned to a semver tag. Refactoring an existing agent should use
Terraform `moved` blocks so the first plan is a no-op for already-owned cloud
resources.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_google"></a> [google](#requirement\_google) | >= 5.0, < 7.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | >= 5.0, < 7.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_secret_manager_secret.credentials](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret) | resource |
| [google_secret_manager_secret_iam_member.credential_accessors](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret_iam_member) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_agent_name"></a> [agent\_name](#input\_agent\_name) | Canonical lowercase agent name, used for labels and default secret names. | `string` | n/a | yes |
| <a name="input_identity"></a> [identity](#input\_identity) | Agent identity contract: human display, GitHub actor, commit attribution, and auth class. | <pre>object({<br/>    display_name     = string<br/>    github_actor     = string<br/>    committer_name   = string<br/>    committer_email  = string<br/>    auth_class       = string<br/>    oauth_secret_ids = optional(list(string), [])<br/>  })</pre> | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID that owns the agent credential secrets. | `string` | n/a | yes |
| <a name="input_runtime"></a> [runtime](#input\_runtime) | Hermes runtime shape for the agent. Kubernetes resources remain rendered by Helm/GitOps consumers. | <pre>object({<br/>    namespace            = string<br/>    service_account_name = optional(string)<br/>    hermes_image         = string<br/>    os_user              = optional(string, "hermes")<br/>    image_pull_secret    = optional(string, "ghcr-pull")<br/>    resources = object({<br/>      requests = map(string)<br/>      limits   = map(string)<br/>    })<br/>    storage = object({<br/>      class = string<br/>      size  = string<br/>    })<br/>  })</pre> | n/a | yes |
| <a name="input_capabilities"></a> [capabilities](#input\_capabilities) | Declared capabilities loaded into the agent runtime. | <pre>object({<br/>    skills = optional(list(string), [])<br/>    mcp_servers = optional(map(object({<br/>      enabled           = optional(bool, true)<br/>      config_secret_ids = optional(list(string), [])<br/>    })), {})<br/>  })</pre> | `{}` | no |
| <a name="input_create_gsm_secrets"></a> [create\_gsm\_secrets](#input\_create\_gsm\_secrets) | When true, create Google Secret Manager secret shells for credentials with create=true. | `bool` | `true` | no |
| <a name="input_credentials"></a> [credentials](#input\_credentials) | Credential secret declarations. Secret values are seeded out-of-band into GSM; this module creates secret shells and IAM only. | <pre>map(object({<br/>    remote_secret_id   = optional(string)<br/>    target_secret_name = optional(string)<br/>    create             = optional(bool, true)<br/>    accessor_members   = optional(list(string), [])<br/>    labels             = optional(map(string), {})<br/>    keys = optional(list(object({<br/>      secret_key      = string<br/>      remote_property = optional(string)<br/>    })), [])<br/>  }))</pre> | `{}` | no |
| <a name="input_cron"></a> [cron](#input\_cron) | Recurring duties owned by the agent. | <pre>map(object({<br/>    schedule    = string<br/>    command     = string<br/>    suspend     = optional(bool, false)<br/>    sla_minutes = optional(number)<br/>  }))</pre> | `{}` | no |
| <a name="input_external_secret"></a> [external\_secret](#input\_external\_secret) | ExternalSecrets contract defaults for Kubernetes consumers. | <pre>object({<br/>    store_name       = optional(string, "gcp-secret-manager")<br/>    store_kind       = optional(string, "ClusterSecretStore")<br/>    refresh_interval = optional(string, "1h")<br/>  })</pre> | `{}` | no |
| <a name="input_guardrails"></a> [guardrails](#input\_guardrails) | Enforcement hooks and policy limits that define what the agent may not do. | <pre>object({<br/>    enforcement_hooks  = optional(list(string), [])<br/>    approvals_required = optional(list(string), [])<br/>    forbidden_actions = optional(list(string), [<br/>      "imperative-infra-mutation",<br/>      "print-secret-values",<br/>    ])<br/>  })</pre> | `{}` | no |
| <a name="input_knowledge"></a> [knowledge](#input\_knowledge) | Agent-owned memory/wiki surfaces and domains. | <pre>object({<br/>    memory_pvc    = optional(string)<br/>    wiki_pvc      = optional(string)<br/>    owned_domains = optional(list(string), [])<br/>  })</pre> | `{}` | no |
| <a name="input_labels"></a> [labels](#input\_labels) | Labels applied to created GSM secrets. | `map(string)` | `{}` | no |
| <a name="input_lane"></a> [lane](#input\_lane) | Queue and issue sources this agent drains. | <pre>object({<br/>    queue_name       = optional(string)<br/>    priority_sources = optional(list(string), [])<br/>    issue_repos      = optional(list(string), [])<br/>  })</pre> | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_agent_contract"></a> [agent\_contract](#output\_agent\_contract) | Normalized agent/employee contract for Helm, GitOps, and drift-review consumers. |
| <a name="output_credential_secret_ids"></a> [credential\_secret\_ids](#output\_credential\_secret\_ids) | Credential name to GSM secret ID map. |
| <a name="output_credential_secret_names"></a> [credential\_secret\_names](#output\_credential\_secret\_names) | Credential name to GSM resource name map for secrets created by this module. |
| <a name="output_external_secret_specs"></a> [external\_secret\_specs](#output\_external\_secret\_specs) | Normalized ExternalSecret sync specs for Kubernetes chart consumers. |
<!-- END_TF_DOCS -->
