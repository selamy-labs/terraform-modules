terraform {
  required_version = ">= 1.8.0, < 2.0.0"
}

module "managed_agents" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/gemini-managed-agents?ref=v0.9.0"

  project_id = "example-project-12345"
  manifest_paths = {
    document_reviewer = "${path.module}/agents/document-reviewer/agent.json"
  }
}

output "active_agent" {
  value = module.managed_agents.active_agents.document_reviewer
}
