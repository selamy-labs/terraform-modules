mock_provider "google" {}

variables {
  project_id = "test-project-123456"
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
    os_user      = "hermes"
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
    mcp_servers = {
      github = {
        enabled           = true
        config_secret_ids = ["reid-gh-token"]
      }
    }
  }

  knowledge = {
    memory_pvc    = "reid-data"
    wiki_pvc      = "reid-wiki"
    owned_domains = ["tax", "credit"]
  }

  credentials = {
    github_token = {
      remote_secret_id   = "reid-gh-token"
      target_secret_name = "reid-credentials"
      accessor_members   = ["serviceAccount:external-secrets@test-project-123456.iam.gserviceaccount.com"]
      keys = [{
        secret_key = "GH_TOKEN"
      }]
    }
    freetaxusa = {
      remote_secret_id = "reid-freetaxusa-credentials"
      create           = false
      keys = [{
        secret_key      = "credentials.json"
        remote_property = "credentials.json"
      }]
    }
  }

  cron = {
    daily_review = {
      schedule    = "0 13 * * *"
      command     = "python3 /opt/scripts/reid_daily_review.py"
      sla_minutes = 60
    }
  }

  lane = {
    queue_name       = "laneq"
    priority_sources = ["finance"]
    issue_repos      = ["selamy-labs/reid"]
  }
}

run "creates_declared_credential_secret_shells" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret.credentials) == 1
    error_message = "Expected only credentials with create=true to create GSM secret shells."
  }

  assert {
    condition     = google_secret_manager_secret.credentials["github_token"].secret_id == "reid-gh-token"
    error_message = "GitHub token secret ID mismatch."
  }
}

run "creates_accessor_bindings" {
  command = plan

  assert {
    condition     = length(google_secret_manager_secret_iam_member.credential_accessors) == 1
    error_message = "Expected one accessor binding."
  }
}

run "emits_agent_contract" {
  command = plan

  assert {
    condition     = output.agent_contract.identity.github_actor == "reid-max"
    error_message = "Agent contract did not preserve GitHub actor."
  }

  assert {
    condition     = output.external_secret_specs.github_token.keys[0].secret_key == "GH_TOKEN"
    error_message = "ExternalSecret spec did not preserve target key."
  }

  assert {
    condition     = output.agent_contract.guardrails.forbidden_actions[0] == "imperative-infra-mutation"
    error_message = "Default guardrail missing."
  }
}
