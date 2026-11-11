output "inventory_path" {
  value = local_file.inventory.filename
}
output "config_path" {
  value = local_file.operations_config.filename
}
