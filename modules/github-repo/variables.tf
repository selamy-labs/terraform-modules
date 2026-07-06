variable "name" {
  description = "Repository name."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9._-]{1,100}$", var.name))
    error_message = "Repository name must be 1-100 chars of [a-zA-Z0-9._-]."
  }
}

variable "description" {
  description = "Repository description."
  type        = string
  default     = ""
}

variable "visibility" {
  description = "Repository visibility: public or private."
  type        = string
  default     = "private"

  validation {
    condition     = contains(["public", "private"], var.visibility)
    error_message = "visibility must be 'public' or 'private'."
  }
}

variable "has_issues" {
  description = "Enable issues."
  type        = bool
  default     = true
}

variable "has_projects" {
  description = "Enable projects."
  type        = bool
  default     = false
}

variable "has_wiki" {
  description = "Enable wiki."
  type        = bool
  default     = false
}

variable "has_discussions" {
  description = "Enable discussions."
  type        = bool
  default     = false
}

variable "is_template" {
  description = "Whether this repo is a template."
  type        = bool
  default     = false
}

variable "homepage_url" {
  description = "Homepage URL."
  type        = string
  default     = ""
}

variable "topics" {
  description = "Repository topics."
  type        = list(string)
  default     = []
}

variable "auto_init" {
  description = "Auto-initialize with a README."
  type        = bool
  default     = true
}

variable "allow_merge_commit" {
  description = "Allow merge commits."
  type        = bool
  default     = false
}

variable "allow_squash_merge" {
  description = "Allow squash merges."
  type        = bool
  default     = true
}

variable "allow_rebase_merge" {
  description = "Allow rebase merges."
  type        = bool
  default     = false
}

variable "allow_auto_merge" {
  description = "Allow auto-merge."
  type        = bool
  default     = true
}

variable "delete_branch_on_merge" {
  description = "Delete branches on merge."
  type        = bool
  default     = true
}

variable "squash_merge_commit_title" {
  description = "Squash merge commit title: PR_TITLE or COMMIT_OR_PR_TITLE."
  type        = string
  default     = "PR_TITLE"
}

variable "squash_merge_commit_message" {
  description = "Squash merge commit message: PR_BODY, COMMIT_MESSAGES, or BLANK."
  type        = string
  default     = "PR_BODY"
}

variable "vulnerability_alerts" {
  description = "Enable Dependabot vulnerability alerts."
  type        = bool
  default     = true
}

variable "template_repository" {
  description = "Template repository to use. Set to null to skip."
  type = object({
    owner      = string
    repository = string
  })
  default = null
}

# Branch protection
variable "default_branch" {
  description = "Default branch name."
  type        = string
  default     = "main"
}

variable "branch_protection_enabled" {
  description = "Enable branch protection on the default branch."
  type        = bool
  default     = true
}

variable "branch_protection_enforce_admins" {
  description = "Enforce branch protection for admins."
  type        = bool
  default     = false
}

variable "required_linear_history" {
  description = "Require linear history."
  type        = bool
  default     = true
}

variable "require_conversation_resolution" {
  description = "Require conversation resolution before merge."
  type        = bool
  default     = false
}

variable "required_status_checks" {
  description = "List of required status check context names."
  type        = list(string)
  default     = []
}

variable "strict_status_checks" {
  description = "Require branches to be up to date before merging when status checks are required."
  type        = bool
  default     = true
}

variable "required_approving_review_count" {
  description = "Number of required approving reviews. Set to 0 to disable."
  type        = number
  default     = 0

  validation {
    condition     = var.required_approving_review_count >= 0 && var.required_approving_review_count <= 6
    error_message = "required_approving_review_count must be 0-6."
  }
}
