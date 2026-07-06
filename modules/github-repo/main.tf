resource "github_repository" "this" {
  name        = var.name
  description = var.description
  visibility  = var.visibility

  has_issues      = var.has_issues
  has_projects    = var.has_projects
  has_wiki        = var.has_wiki
  has_discussions = var.has_discussions
  is_template     = var.is_template
  homepage_url    = var.homepage_url
  topics          = var.topics

  auto_init                   = var.auto_init
  allow_merge_commit          = var.allow_merge_commit
  allow_squash_merge          = var.allow_squash_merge
  allow_rebase_merge          = var.allow_rebase_merge
  allow_auto_merge            = var.allow_auto_merge
  delete_branch_on_merge      = var.delete_branch_on_merge
  squash_merge_commit_title   = var.squash_merge_commit_title
  squash_merge_commit_message = var.squash_merge_commit_message

  archive_on_destroy = true

  vulnerability_alerts = var.vulnerability_alerts

  dynamic "template" {
    for_each = var.template_repository != null ? [var.template_repository] : []
    content {
      owner      = template.value.owner
      repository = template.value.repository
    }
  }
}

resource "github_branch_protection" "default" {
  count = var.branch_protection_enabled ? 1 : 0

  repository_id = github_repository.this.node_id
  pattern       = var.default_branch

  enforce_admins                  = var.branch_protection_enforce_admins
  required_linear_history         = var.required_linear_history
  require_conversation_resolution = var.require_conversation_resolution
  allows_force_pushes             = false
  allows_deletions                = false

  dynamic "required_status_checks" {
    for_each = length(var.required_status_checks) > 0 ? [true] : []
    content {
      strict   = var.strict_status_checks
      contexts = var.required_status_checks
    }
  }

  dynamic "required_pull_request_reviews" {
    for_each = var.required_approving_review_count > 0 ? [true] : []
    content {
      required_approving_review_count = var.required_approving_review_count
      dismiss_stale_reviews           = true
    }
  }
}
