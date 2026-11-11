# Terraform provisions local configuration files, not cloud servers.
resource "local_file" "inventory" {
  filename = "${path.module}/generated/infrastructure-inventory.json"
  content = jsonencode({
    project = "gts-operations-hub"
    environment = var.environment
    managed_by = "terraform"
    assets = ["gts-api", "gts-database", "identity-provider"]
  })
}

resource "local_file" "operations_config" {
  filename = "${path.module}/generated/operations-config.txt"
  content = "Environment: ${var.environment}\nOwner: ${var.owner}\nManaged by Terraform\n"
}
