data "external" "manifest" {
  for_each = local.manifest_paths

  program = [var.python_executable, local.reconciler_path, "render"]

  query = {
    manifest_path = each.value
  }
}

data "external" "revision_status" {
  for_each = var.enable_remote_read ? local.revisions : {}

  program = [var.python_executable, local.reconciler_path, "read"]

  query = {
    project_id                     = var.project_id
    manifest_path                  = each.value.manifest_path
    revision_key                   = each.value.revision_key
    authentication_mode            = var.authentication.mode
    api_key_secret_manager_version = var.authentication.api_key_secret_manager_version == null ? "" : var.authentication.api_key_secret_manager_version
    managed_instance_id            = terraform_data.revision[each.key].id
  }
}
