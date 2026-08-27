locals {
  reconciler_path = "${path.module}/reconciler/agentctl.py"
  manifest_paths = {
    for key, value in var.manifest_paths : key => startswith(value, "/") ? value : abspath("${path.root}/${value}")
  }
  source_manifests = {
    for key, path in local.manifest_paths : key => jsondecode(file(path))
  }

  rendered_manifests = {
    for key, rendered in data.external.manifest : key => jsondecode(rendered.result.manifest_json)
  }

  revision_candidates = flatten([
    for manifest_key, manifest in local.rendered_manifests : [
      for revision_key, revision in manifest.revisions : merge(revision, {
        manifest_key  = manifest_key
        manifest_path = local.manifest_paths[manifest_key]
        revision_key  = revision_key
        active        = manifest.active_revision == revision_key
      })
    ]
  ])

  # Resource identity follows the content-addressed remote identity, not
  # caller-selected map or revision labels. Group first so a duplicate remote
  # owner becomes an explicit failing precondition instead of a duplicate-key
  # expression error or two resources racing to create/delete the same agent.
  revision_groups = {
    for revision in local.revision_candidates : revision.agent_id => revision...
  }

  revisions = {
    for agent_id, owners in local.revision_groups : agent_id => merge(owners[0], {
      owner_count = length(owners)
      owner_paths = [for owner in owners : "${owner.manifest_key}/${owner.revision_key}"]
      # Read this lifecycle-only control directly from source so a rapid
      # declared repair cannot be hidden by an external data-source refresh.
      reconcile_generation = try(
        local.source_manifests[owners[0].manifest_key].spec.revisions[owners[0].revision_key].lifecycle.reconcile_generation,
        0,
      )
      reconcile_generation_valid = (
        can(local.source_manifests[owners[0].manifest_key].spec.revisions[owners[0].revision_key])
        && can(regex(
          "^(0|[1-9][0-9]*)$",
          jsonencode(try(
            local.source_manifests[owners[0].manifest_key].spec.revisions[owners[0].revision_key].lifecycle.reconcile_generation,
            0,
          )),
        ))
      )
    })
  }

  active_agents = {
    for manifest_key, manifest in local.rendered_manifests : manifest_key => {
      agent_id              = manifest.revisions[manifest.active_revision].agent_id
      revision              = manifest.active_revision
      revision_digest       = manifest.revisions[manifest.active_revision].revision_digest
      model                 = manifest.revisions[manifest.active_revision].model
      output_schema_path    = manifest.revisions[manifest.active_revision].output_schema_path
      output_schema_digest  = manifest.revisions[manifest.active_revision].output_schema_digest
      evaluation_case_paths = manifest.revisions[manifest.active_revision].evaluation_case_paths
      labels                = manifest.labels
      annotations           = manifest.annotations
    }
  }
}
