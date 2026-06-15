locals {
  gke_wif_member = (
    var.wif_k8s_namespace != null && var.wif_k8s_service_account != null
    ? "serviceAccount:${var.project_id}.svc.id.goog[${var.wif_k8s_namespace}/${var.wif_k8s_service_account}]"
    : null
  )

  wif_pool_member = (
    var.wif_pool_provider != null
    ? "principalSet://iam.googleapis.com/${var.wif_pool_provider}/*"
    : null
  )

  wif_members = compact(concat(
    [local.gke_wif_member, local.wif_pool_member],
    var.additional_wif_members,
  ))
}
