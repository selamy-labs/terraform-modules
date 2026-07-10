# Terraform Modules System Context

This repository publishes reusable OpenTofu modules as semver-pinned Git
sources. Consumer repositories choose a module, provide environment-specific
inputs, and own planning and applying it; this repository does not apply
infrastructure itself.

```mermaid
flowchart LR
    consumers["Consumer repositories and stacks"]
    source["Semver-pinned Git module source"]
    identity["Identity and secrets<br/>agent, gcp-sa-wif, gsm-secret"]
    governance["Governance and observability<br/>github-repo, monitoring-policy"]
    runners["Runner infrastructure<br/>runner-cluster, oci-oke"]
    providers["OpenTofu provider APIs"]
    resources["GCP, GitHub, OCI, runner substrates"]
    outputs["Typed module outputs"]

    consumers --> source
    source --> identity
    source --> governance
    source --> runners
    identity --> providers
    governance --> providers
    runners --> providers
    providers --> resources
    identity --> outputs
    governance --> outputs
    runners --> outputs
    outputs --> consumers
```

## Boundaries

- Module source, variables, outputs, provider constraints, tests, and generated
  module documentation live in this repository.
- Consumers pin immutable release tags and own backend state, provider
  credentials, plans, applies, and rollbacks.
- Cloud and platform APIs create the real resources; this repository contains no
  live state or credentials.
- CI formats, lints, validates, security-scans, tests, and checks generated
  documentation without applying infrastructure.
