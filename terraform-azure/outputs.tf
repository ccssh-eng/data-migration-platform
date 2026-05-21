output "sql_server_name" {
  value = azurerm_mssql_server.sql_server.name
}

output "database_name" {
  value = azurerm_mssql_database.db.name
}
