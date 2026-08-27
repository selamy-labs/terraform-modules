output "active_agents" {
  description = "Invocation contract for each manifest's declared active immutable revision."
  value       = local.active_agents
}

output "revisions" {
  description = "All declared immutable revisions keyed by content-addressed remote agent ID."
  value = {
    for key, revision in local.revisions : key => {
      active               = revision.active
      agent_id             = revision.agent_id
      model                = revision.model
      revision_digest      = revision.revision_digest
      output_schema_path   = revision.output_schema_path
      output_schema_digest = revision.output_schema_digest
      reconcile_generation = revision.reconcile_generation
      deletion_policy      = revision.deletion_policy
    }
  }
}

output "drift_report" {
  description = "Remote read result for each declared revision. Drift repair is an explicit reconcile_generation manifest change."
  value = var.enable_remote_read ? {
    for key, status in data.external.revision_status : key => {
      status          = status.result.status
      agent_id        = status.result.agent_id
      expected_digest = status.result.expected_digest
      observed_digest = status.result.observed_digest
    }
  } : {}
}
