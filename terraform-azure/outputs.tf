output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "sql_server_name" {
  value = azurerm_mssql_server.sql_server.name
}
