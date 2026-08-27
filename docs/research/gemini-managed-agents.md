# Gemini Developer API managed-agent source decisions

Last verified: 2026-08-27.

This record explains why `modules/gemini-managed-agents` uses a small
command-backed reconciler and which parts of its contract are direct service
constraints. Primary sources win when documentation conflicts.

## Service contract

- [Agents overview](https://ai.google.dev/gemini-api/docs/agents): managed
  agents provision Google-hosted Linux sandboxes. The service is Public Preview,
  allows unrestricted outbound traffic by default, permits up to 1,000 agents,
  expires inactive environments after seven days, and commonly consumes 100k to
  3M tokens per interaction.
- [Building managed agents](https://ai.google.dev/gemini-api/docs/custom-agents):
  named agents are created from instructions, tools, file sources, and a base
  environment. Omitted tools grant Code Execution, Google Search, and URL
  Context by default. The only current base agent is
  `antigravity-preview-05-2026`; the default/current target model is
  `gemini-3.7-flash`. Named-agent model selection cannot be overridden at
  invocation time.
- [Agents API](https://ai.google.dev/api/agents): the REST surface currently
  exposes create, list, get, and delete. It exposes no update operation.
  Environment networking is either `disabled` or an explicit allowlist; omission
  means unrestricted access. Sources may be inline, repository, Cloud Storage,
  or Skill Registry sources. Remote MCP definitions support named servers,
  headers, and allowed tool subsets. The Agent schema also exposes a top-level
  string `system_instruction`; allowlist header transforms may be returned as
  either one object or an array of objects.
- [Agent environments](https://ai.google.dev/gemini-api/docs/agent-environment):
  the sandbox has four CPU cores and 16 GB memory during preview. Inline files
  are limited to 1 MB each and 2 MB total; repositories are limited to 500 MB
  and Cloud Storage sources to 2 GB. Credentials can be injected by the egress
  proxy without entering the sandbox.
- [Antigravity agent](https://ai.google.dev/gemini-api/docs/antigravity-agent)
  and the [Interactions API](https://ai.google.dev/api/interactions-api-v1): a
  named managed agent is invoked with `agent`, `input`, and
  `environment:"remote"`. Background execution supports status reads and
  cancellation, but requires `store:true`; cancellation applies only while a
  background interaction is running. The formal REST reference uses
  `POST /interactions/{id}/cancel`, while the Antigravity guide currently shows
  `POST /interactions/{id}:cancel`, so a live contract probe must settle the
  wire path before an invocation client ships.
- [Interactions API May 2026 migration](https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026):
  current REST responses use `steps`, not the retired `outputs` shape. The
  `output_text` convenience field is SDK-added, so REST consumers must parse
  the typed `steps` payload. The current structured-output request shape for
  model interactions is `response_format` with `type:"text"`,
  `mime_type:"application/json"`, and `schema`.
- [OAuth quickstart](https://ai.google.dev/gemini-api/docs/oauth): OAuth and ADC
  are supported for stricter access control. The documented scopes are
  `cloud-platform` and `generative-language.retriever`.
- [API key guide](https://ai.google.dev/gemini-api/docs/api-key): API keys are
  project-bound. Google recommends authorization keys bound to a service
  account for platforms and documents that legacy Standard keys will be
  rejected by the Gemini API beginning in September 2026.
- [Partner integration](https://ai.google.dev/gemini-api/docs/partner-integration):
  libraries and platforms must send `x-goog-api-client` in
  `company-product/version` form. The reconciler sends a release-versioned,
  neutral client identifier on every Agents API request.
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing) and
  [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits): paid usage
  is metered by model tokens and tool usage, while a free tier has its own rate
  limit and quota. A managed interaction can consume tokens across many
  reasoning loops. Sandbox compute is not billed during preview. Limits are
  project-level and dynamic.
- [Billing](https://ai.google.dev/gemini-api/docs/billing): Gemini API Prepay
  and Postpay plans took effect on 2026-03-23. For paid-tier deployments, a
  Cloud Billing link alone does not prove that the Gemini API paid service will
  accept calls. Prepay projects require a positive prepaid-credit balance, and
  the current plan/status is reported by Google AI Studio. A live authenticated
  API read is therefore a paid-environment release gate in addition to the
  Cloud Billing project-link check.
- [Additional terms](https://ai.google.dev/gemini-api/terms) and
  [zero data retention](https://ai.google.dev/gemini-api/docs/zdr): paid-service
  prompts and responses are not used to improve Google products, but limited
  abuse-monitoring retention remains. Interactions store state by default unless
  callers set `store:false`; background agent execution cannot use that
  stateless mode. This module never invokes interactions.

## Conflicts resolved

1. The overview previously described Gemini 3.6 Flash as the default, while the
   newer custom-agent guide and API reference name Gemini 3.7 Flash. The module
   follows the newer, endpoint-specific sources and still requires the model to
   be explicit.
2. The custom-agent guide says to “update the agent definition,” but the current
   API reference exposes no update endpoint and separately states that native
   versioning and rollback do not exist. The module therefore creates immutable,
   content-addressed IDs and treats any same-ID drift as delete-and-recreate.
3. Deleting an agent does not delete already-created environments or
   interactions. The module manages agent definitions only and makes no broader
   cleanup claim.
4. The general Interactions request exposes instruction and tool fields, and the
   managed-agent guide shows invocation-time environment overrides. Named-agent
   model selection is locked. Consumers that need the declared revision to be
   the complete behavior boundary must omit every invocation-time behavior or
   environment override; the module cannot enforce caller behavior.
5. The API accepts repository and Cloud Storage sources but does not expose an
   integrity field or a documented immutable revision selector. This module's
   initial schema therefore mounts only locally hashed, version-controlled
   runtime files. Remote source support must not be added until the reconciler
   can prove the fetched bytes match the declared revision.
6. The Antigravity prose guide describes MCP `allowed_tools` as a flat list of
   names, while the current Agents REST/OpenAPI contract types it as an array of
   `AllowedTools` policy objects. REST is the reconciler boundary, so the module
   emits one `{ "mode": "auto", "tools": [...] }` policy and guards that wire
   shape in its strict contract fake.
7. The API accepts an allowlist header transform as either a single object or a
   list of objects. The module emits the simpler object form. Drift comparison
   accepts the service-normalized single-item list as equivalent, while a
   multi-item or malformed transform fails closed as redacted drift.
8. The top-level `system_instruction` is additive with mounted
   `.agents/AGENTS.md`. The normalized manifest therefore requires a
   revision-relative system-instruction file and hashes both instruction
   surfaces into the immutable revision rather than relying on an unmanaged
   console field.
9. Managed agents are available under both free-tier quota and paid
   pay-as-you-go terms. For a paid-tier deployment, Cloud Billing can report a
   project as billing-enabled while its Gemini API plan is not yet eligible to
   serve paid calls or a Prepay balance is empty. The module supports either
   tier and deliberately does not manage payments. Paid-tier operators must
   verify the AI Studio plan/status and an authenticated Agents API read before
   treating an environment as ready.
10. The general Interactions schema documents JSON structured output, but the
    newer, agent-specific Antigravity limitations explicitly state that managed
    Antigravity execution does not support structured outputs. This module keeps
    the output-schema path and digest as a versioned caller-side validation
    contract. Invocation clients must not send `response_format` for these named
    agents; they must parse the current REST `steps` shape and validate the
    candidate locally. Exact schema conformance remains an empirical agent gate.
11. `store:false` and recoverable background execution are mutually exclusive
    today. A caller choosing ephemeral synchronous execution cannot claim
    provider status recovery or provider-confirmed cancellation after losing
    the response. A caller choosing background execution must explicitly accept
    `store:true`, checkpoint the interaction ID, and own subsequent read,
    cancel, retention, and delete behavior. Those are invocation concerns and
    remain outside this definition-only module.

## Provider and module coverage

- The official `hashicorp/google` and `hashicorp/google-beta` providers were
  inspected at [`v8.0.0`](https://github.com/hashicorp/terraform-provider-google/releases/tag/v8.0.0),
  including their generated resource trees. They contain Agent Registry, Agent
  Gateway, Vertex reasoning-engine, and other unrelated agent resources, but no
  resource for `generativelanguage.googleapis.com/v1beta/agents`.
- [Magic Modules](https://github.com/GoogleCloudPlatform/magic-modules) contains
  no product schema for the Developer API agent collection, confirming the
  absence is upstream rather than documentation lag in one provider build.
- [Cloud Foundation Fabric](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric)
  provides Agent Engine and Agent Gateway modules. Agent Engine deploys Vertex
  AI reasoning engines and ADK/container code; Agent Gateway targets the Agent
  Registry/Gateway control plane. Neither manages this API.
- [genai-factory](https://github.com/GoogleCloudPlatform/genai-factory) builds
  Vertex Agent Engine/ADK and Gemini Enterprise blueprints. It is valuable
  infrastructure guidance but a different runtime and control plane.
- Cloud Foundation Toolkit repositories and public GitHub code/repository
  searches produced no maintained module or HCL use of the Developer API Agents
  endpoint as of the verification date.

Decision: use `terraform_data` plus `hashicorp/external` `2.4.1` and a repo-owned
Python reconciler. The reconciler is intentionally limited to validation,
canonical rendering, authentication, secret retrieval, CRUD, remote comparison,
and post-action verification. Native provider adoption should remove it without
changing the normalized manifest directories or active-revision contract.

### Reproducible discovery ledger

The following upstream heads were inspected on 2026-08-27; the commit pins make
the negative result reproducible even as the repositories move:

| Source | Inspected revision | Why it was not adopted |
| --- | --- | --- |
| [Cloud Foundation Fabric](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric) | `74ccc8a3d53315dd7ad9eeaad9362a21f6d7a9fc` | Its Agent Engine and Agent Gateway modules target Vertex/ADK and Network Services. |
| [CFT Agent Gateway](https://github.com/GoogleCloudPlatform/terraform-google-agent-gateway) | `dad7669e4e23c0fd3522cbba68a958ee4f3e31a5` | Manages `google_network_services_agent_gateway`, not Developer API agent definitions. |
| [CFT Agent Registry](https://github.com/GoogleCloudPlatform/terraform-google-agent-registry) | `211159c816a33423f9c585a8f499ba485965e69e` | Manages the separate `agentregistry.googleapis.com` catalog/control plane. |
| [genai-factory](https://github.com/GoogleCloudPlatform/genai-factory) | `8a2d3249632b0ad4ea4b47000e4be4b15f68440d` | Deploys Vertex Agent Engine, ADK, or custom Cloud Run applications. |
| [Google provider](https://github.com/hashicorp/terraform-provider-google) | `3e6a35620368a9ee316901eca8c48fd11c70b2a9` | No Developer API Agents resource. |
| [Magic Modules](https://github.com/GoogleCloudPlatform/magic-modules) | `a712ca503051cb20f403f7dd69a9500797dbb53e` | No product schema for the Developer API endpoint. |

GitHub code search returned zero HCL and zero `.tf` files containing the exact
`generativelanguage.googleapis.com/v1beta/agents` endpoint. Repository searches
for `terraform gemini managed agents`, `terraform google gemini agent`,
`opentofu gemini agent`, and `terraform generative language agents` also
returned zero repositories. Consequently there was no reputable community
module implementing this API to review or adopt; similarly named results target
Vertex, ADK, Dialogflow, or another vendor's agent service.
