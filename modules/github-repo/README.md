# github-repo

Creates a GitHub repository with default settings and optional branch protection. Designed to declaratively manage repositories like terraform-modules and helm-charts.

## Usage

```hcl
module "my_repo" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/github-repo?ref=v0.1.0"

  name        = "my-repo"
  description = "Managed by OpenTofu"
  visibility  = "private"

  branch_protection_enabled = true
  required_status_checks    = ["ci / lint"]
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_github"></a> [github](#requirement\_github) | ~> 6.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_github"></a> [github](#provider\_github) | ~> 6.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [github_branch_protection.default](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/branch_protection) | resource |
| [github_repository.this](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_name"></a> [name](#input\_name) | Repository name. | `string` | n/a | yes |
| <a name="input_allow_auto_merge"></a> [allow\_auto\_merge](#input\_allow\_auto\_merge) | Allow auto-merge. | `bool` | `true` | no |
| <a name="input_allow_merge_commit"></a> [allow\_merge\_commit](#input\_allow\_merge\_commit) | Allow merge commits. | `bool` | `false` | no |
| <a name="input_allow_rebase_merge"></a> [allow\_rebase\_merge](#input\_allow\_rebase\_merge) | Allow rebase merges. | `bool` | `false` | no |
| <a name="input_allow_squash_merge"></a> [allow\_squash\_merge](#input\_allow\_squash\_merge) | Allow squash merges. | `bool` | `true` | no |
| <a name="input_auto_init"></a> [auto\_init](#input\_auto\_init) | Auto-initialize with a README. | `bool` | `true` | no |
| <a name="input_branch_protection_enabled"></a> [branch\_protection\_enabled](#input\_branch\_protection\_enabled) | Enable branch protection on the default branch. | `bool` | `true` | no |
| <a name="input_branch_protection_enforce_admins"></a> [branch\_protection\_enforce\_admins](#input\_branch\_protection\_enforce\_admins) | Enforce branch protection for admins. | `bool` | `false` | no |
| <a name="input_default_branch"></a> [default\_branch](#input\_default\_branch) | Default branch name. | `string` | `"main"` | no |
| <a name="input_delete_branch_on_merge"></a> [delete\_branch\_on\_merge](#input\_delete\_branch\_on\_merge) | Delete branches on merge. | `bool` | `true` | no |
| <a name="input_description"></a> [description](#input\_description) | Repository description. | `string` | `""` | no |
| <a name="input_has_discussions"></a> [has\_discussions](#input\_has\_discussions) | Enable discussions. | `bool` | `false` | no |
| <a name="input_has_issues"></a> [has\_issues](#input\_has\_issues) | Enable issues. | `bool` | `true` | no |
| <a name="input_has_projects"></a> [has\_projects](#input\_has\_projects) | Enable projects. | `bool` | `false` | no |
| <a name="input_has_wiki"></a> [has\_wiki](#input\_has\_wiki) | Enable wiki. | `bool` | `false` | no |
| <a name="input_homepage_url"></a> [homepage\_url](#input\_homepage\_url) | Homepage URL. | `string` | `""` | no |
| <a name="input_is_template"></a> [is\_template](#input\_is\_template) | Whether this repo is a template. | `bool` | `false` | no |
| <a name="input_require_conversation_resolution"></a> [require\_conversation\_resolution](#input\_require\_conversation\_resolution) | Require conversation resolution before merge. | `bool` | `false` | no |
| <a name="input_required_approving_review_count"></a> [required\_approving\_review\_count](#input\_required\_approving\_review\_count) | Number of required approving reviews. Set to 0 to disable. | `number` | `0` | no |
| <a name="input_required_linear_history"></a> [required\_linear\_history](#input\_required\_linear\_history) | Require linear history. | `bool` | `true` | no |
| <a name="input_required_status_checks"></a> [required\_status\_checks](#input\_required\_status\_checks) | List of required status check context names. | `list(string)` | `[]` | no |
| <a name="input_squash_merge_commit_message"></a> [squash\_merge\_commit\_message](#input\_squash\_merge\_commit\_message) | Squash merge commit message: PR\_BODY, COMMIT\_MESSAGES, or BLANK. | `string` | `"PR_BODY"` | no |
| <a name="input_squash_merge_commit_title"></a> [squash\_merge\_commit\_title](#input\_squash\_merge\_commit\_title) | Squash merge commit title: PR\_TITLE or COMMIT\_OR\_PR\_TITLE. | `string` | `"PR_TITLE"` | no |
| <a name="input_template_repository"></a> [template\_repository](#input\_template\_repository) | Template repository to use. Set to null to skip. | <pre>object({<br/>    owner      = string<br/>    repository = string<br/>  })</pre> | `null` | no |
| <a name="input_topics"></a> [topics](#input\_topics) | Repository topics. | `list(string)` | `[]` | no |
| <a name="input_visibility"></a> [visibility](#input\_visibility) | Repository visibility: public or private. | `string` | `"private"` | no |
| <a name="input_vulnerability_alerts"></a> [vulnerability\_alerts](#input\_vulnerability\_alerts) | Enable Dependabot vulnerability alerts. | `bool` | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_full_name"></a> [full\_name](#output\_full\_name) | The full name of the repository (owner/name). |
| <a name="output_html_url"></a> [html\_url](#output\_html\_url) | The URL to the repository on GitHub. |
| <a name="output_http_clone_url"></a> [http\_clone\_url](#output\_http\_clone\_url) | HTTPS clone URL. |
| <a name="output_node_id"></a> [node\_id](#output\_node\_id) | The GraphQL node ID of the repository. |
| <a name="output_repo_id"></a> [repo\_id](#output\_repo\_id) | The numeric ID of the repository. |
| <a name="output_ssh_clone_url"></a> [ssh\_clone\_url](#output\_ssh\_clone\_url) | SSH clone URL. |
<!-- END_TF_DOCS -->
