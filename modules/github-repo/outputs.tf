output "full_name" {
  description = "The full name of the repository (owner/name)."
  value       = github_repository.this.full_name
}

output "html_url" {
  description = "The URL to the repository on GitHub."
  value       = github_repository.this.html_url
}

output "ssh_clone_url" {
  description = "SSH clone URL."
  value       = github_repository.this.ssh_clone_url
}

output "http_clone_url" {
  description = "HTTPS clone URL."
  value       = github_repository.this.http_clone_url
}

output "node_id" {
  description = "The GraphQL node ID of the repository."
  value       = github_repository.this.node_id
}

output "repo_id" {
  description = "The numeric ID of the repository."
  value       = github_repository.this.repo_id
}
