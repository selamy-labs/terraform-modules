variables {
  project_id = "example-project-12345"
  manifest_paths = {
    test_worker = "tests/fixtures/agents/test-worker/agent.json"
  }
  enable_remote_read = false
}

run "plans_immutable_revision" {
  command = plan

  assert {
    condition     = startswith(output.active_agents.test_worker.agent_id, "test-worker-")
    error_message = "Expected a content-addressed test-worker agent ID."
  }

  assert {
    condition     = output.active_agents.test_worker.model == "gemini-3.7-flash"
    error_message = "Expected the declared reasoning model."
  }

  assert {
    condition     = length(output.active_agents.test_worker.revision_digest) == 64
    error_message = "Expected a full SHA-256 revision digest."
  }

  assert {
    condition     = output.drift_report == {}
    error_message = "Offline plans must not perform remote reads."
  }
}
