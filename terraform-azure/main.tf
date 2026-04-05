provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-data-migration-demo"
  location = "France Central"
}

resource "azurerm_storage_account" "storage" {
  name                     = "datamigrationdemo123"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_mssql_server" "sql_server" {
  name                         = "migration-sql-server-demo"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = "adminuser"
  administrator_login_password = "YourPassword123!"
}

resource "azurerm_mssql_database" "db" {
  name           = "migrationdb"
  server_id      = azurerm_mssql_server.sql_server.id
  sku_name       = "Basic"
}
