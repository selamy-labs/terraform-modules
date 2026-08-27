# New-repo bootstrap: ingest canonical IaC by default

Every new Selamy repo that provisions cloud/k8s resources MUST consume the
canonical shared IaC instead of home-rolling its own modules or charts. This is
the default, not an option — duplicated private runner and delivery modules are
the failure mode this policy prevents (laneq #628).

## Canonical homes

| Concern | Canonical home | How to consume |
|---|---|---|
| GCP secrets, SA/WIF, GitHub repo settings, monitoring policies, ARC runner scale sets | `selamy-labs/terraform-modules` | git source pinned to a semver tag: `?ref=vX.Y.Z` |
| Agent k8s workload (StatefulSet, flagd, ExternalSecrets, cronjobs, RBAC, monitoring, entrypoint) | `selamy-labs/helm-charts` (`selamy-agent-lib` library chart) | Helm dependency pinned to a chart version |

## Terraform / OpenTofu

Never copy a module into the repo. Import it:

```hcl
module "secret" {
  source = "git::https://github.com/selamy-labs/terraform-modules.git//modules/gsm-secret?ref=v0.3.0"
  # ...
}

```

Available modules: `gsm-secret`, `gcp-sa-wif`, `github-repo`, `monitoring-policy`. (The ARC runner-scale-set module now lives in the public [speedforge/terraform-modules](https://github.com/speedforge/terraform-modules) repo: `git::https://github.com/speedforge/terraform-modules.git//modules/arc-runner-scale-set?ref=v0.1.0`.) If a shape you need is missing, ADD it to `terraform-modules` (strict module file-structure + tests + `tofu validate`/`tofu test` + a new tag) — do not inline it.

## Helm (agent workloads)

In the agent chart's `Chart.yaml`:

```yaml
dependencies:
  - name: selamy-agent-lib
    version: "0.1.6"
    repository: "oci://ghcr.io/selamy-labs/charts"
```

Then render the named templates instead of hand-writing the manifests:

```yaml
{{ include "selamy.entrypoint.configmap" . }}
---
{{ include "selamy.statefulset" . }}
---
{{ include "selamy.flagd.configmap" . }}
---
{{ include "selamy.externalsecret.ghtoken" . }}
---
{{ include "selamy.externalsecret.generic" . }}   # codex-auth, google-client, ghcr-pull, ...
---
{{ include "selamy.cronjobObserver.rbac" . }}
---
{{- range $name, $job := .Values.cronJobs }}{{- if $job.enabled }}
---
{{ include "selamy.cronjob.scheduled" (dict "root" $ "name" $name "job" $job) }}
{{- end }}{{- end }}
```

If a workload shape is missing from the library, ADD it to `helm-charts` (template + values + schema + consumer unittest) — do not fork the chart.

## The rule

- Home-rolled IaC that duplicates a canonical module/chart is a defect; reviewers should block it.
- The only inlined IaC allowed is genuinely repo-specific infra with no canonical equivalent (e.g. a one-off GKE cluster definition).
- Bumping a canonical version is a deliberate `?ref=`/`version:` change + re-plan/re-render.
