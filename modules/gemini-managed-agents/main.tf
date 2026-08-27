resource "terraform_data" "revision" {
  for_each = local.revisions

  input = {
    agent_id                       = each.value.agent_id
    authentication_mode            = var.authentication.mode
    api_key_secret_manager_version = var.authentication.api_key_secret_manager_version == null ? "" : var.authentication.api_key_secret_manager_version
    deletion_policy                = each.value.deletion_policy
    manifest_path                  = each.value.manifest_path
    python_executable              = var.python_executable
    project_id                     = var.project_id
    reconcile_generation           = each.value.reconcile_generation
    reconciler_source              = file(local.reconciler_path)
    revision_digest                = each.value.revision_digest
    revision_key                   = each.value.revision_key
  }

  triggers_replace = [
    var.project_id,
    var.authentication.mode,
    var.authentication.api_key_secret_manager_version == null ? "" : var.authentication.api_key_secret_manager_version,
    each.value.revision_digest,
    each.value.reconcile_generation,
  ]

  lifecycle {
    precondition {
      condition     = each.value.owner_count == 1
      error_message = "Each content-addressed agent ID must have exactly one manifest/revision owner; ${each.value.agent_id} is declared by ${join(", ", each.value.owner_paths)}."
    }

    precondition {
      condition     = each.value.reconcile_generation_valid
      error_message = "Every declared lifecycle.reconcile_generation must be a non-negative integer before reconciliation."
    }
  }

  provisioner "local-exec" {
    command = <<-EOT
      exec "$GEMINI_AGENTCTL_PYTHON" "$GEMINI_AGENTCTL_RECONCILER" reconcile \
        --project-id "$GEMINI_AGENTCTL_PROJECT_ID" \
        --manifest-path "$GEMINI_AGENTCTL_MANIFEST_PATH" \
        --revision-key "$GEMINI_AGENTCTL_REVISION_KEY" \
        --authentication-mode "$GEMINI_AGENTCTL_AUTH_MODE" \
        --api-key-secret-manager-version "$GEMINI_AGENTCTL_API_KEY_REF"
    EOT

    environment = {
      GEMINI_AGENTCTL_API_KEY_REF   = var.authentication.api_key_secret_manager_version == null ? "" : var.authentication.api_key_secret_manager_version
      GEMINI_AGENTCTL_AUTH_MODE     = var.authentication.mode
      GEMINI_AGENTCTL_MANIFEST_PATH = each.value.manifest_path
      GEMINI_AGENTCTL_PROJECT_ID    = var.project_id
      GEMINI_AGENTCTL_PYTHON        = var.python_executable
      GEMINI_AGENTCTL_RECONCILER    = local.reconciler_path
      GEMINI_AGENTCTL_REVISION_KEY  = each.value.revision_key
    }
  }

  provisioner "local-exec" {
    when = destroy

    command = <<-EOT
      exec "$GEMINI_AGENTCTL_PYTHON" -c "$GEMINI_AGENTCTL_SOURCE" delete \
        --project-id "$GEMINI_AGENTCTL_PROJECT_ID" \
        --agent-id "$GEMINI_AGENTCTL_AGENT_ID" \
        --deletion-policy "$GEMINI_AGENTCTL_DELETION_POLICY" \
        --authentication-mode "$GEMINI_AGENTCTL_AUTH_MODE" \
        --api-key-secret-manager-version "$GEMINI_AGENTCTL_API_KEY_REF"
    EOT

    environment = {
      GEMINI_AGENTCTL_AGENT_ID        = self.input.agent_id
      GEMINI_AGENTCTL_API_KEY_REF     = self.input.api_key_secret_manager_version
      GEMINI_AGENTCTL_AUTH_MODE       = self.input.authentication_mode
      GEMINI_AGENTCTL_DELETION_POLICY = self.input.deletion_policy
      GEMINI_AGENTCTL_PROJECT_ID      = self.input.project_id
      GEMINI_AGENTCTL_PYTHON          = self.input.python_executable
      GEMINI_AGENTCTL_SOURCE          = self.input.reconciler_source
    }
  }
}
