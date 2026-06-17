resource "helm_release" "this" {
  name             = var.name
  namespace        = var.namespace
  create_namespace = var.create_namespace

  repository = "oci://ghcr.io/actions/actions-runner-controller-charts"
  chart      = "gha-runner-scale-set"
  version    = var.chart_version

  # Typed canonical contract first, then optional raw escape-hatch overrides.
  values = compact([
    local.values_yaml,
    var.extra_values,
  ])
}
