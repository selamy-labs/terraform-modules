locals {
  common_labels = merge(
    {
      managed_by   = "terraform"
      selamy_agent = var.agent_name
      module       = "agent"
    },
    var.labels,
  )

  credential_secret_ids = {
    for name, credential in var.credentials :
    name => coalesce(credential.remote_secret_id, "${var.agent_name}-${name}")
  }

  creatable_credentials = {
    for name, credential in var.credentials :
    name => credential
    if var.create_gsm_secrets && credential.create
  }

  credential_accessor_bindings = {
    for binding in flatten([
      for credential_name, credential in local.creatable_credentials : [
        for member in credential.accessor_members : {
          key             = "${credential_name}:${member}"
          credential_name = credential_name
          member          = member
        }
      ]
    ]) : binding.key => binding
  }

  external_secret_specs = {
    for name, credential in var.credentials :
    name => {
      target_secret_name = coalesce(credential.target_secret_name, "${var.agent_name}-credentials")
      remote_secret_id   = local.credential_secret_ids[name]
      store_name         = var.external_secret.store_name
      store_kind         = var.external_secret.store_kind
      refresh_interval   = var.external_secret.refresh_interval
      keys               = credential.keys
    }
  }

  agent_contract = {
    agent_name            = var.agent_name
    identity              = var.identity
    runtime               = var.runtime
    capabilities          = var.capabilities
    knowledge             = var.knowledge
    credential_secret_ids = local.credential_secret_ids
    external_secret_specs = local.external_secret_specs
    cron                  = var.cron
    lane                  = var.lane
    guardrails            = var.guardrails
  }
}
