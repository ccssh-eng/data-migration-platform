# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Random suffix pour noms uniques
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# SQL Server
resource "azurerm_mssql_server" "sql_server" {
  name                         = "sql-${random_string.suffix.result}"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_user
  administrator_login_password = var.sql_admin_password
}

# SQL Database
resource "azurerm_mssql_database" "db" {
  name      = "migration-db"
  server_id = azurerm_mssql_server.sql_server.id
  sku_name  = "Basic"
}

# Storage Account
resource "azurerm_storage_account" "storage" {
  name                     = "st${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Storage Container
resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

# Key Vault
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "kv" {
  name                = "kv-migration-platform"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

resource "azurerm_key_vault_access_policy" "adf_policy" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_data_factory.adf.identity[0].principal_id

  secret_permissions = ["Get", "Set", "List"]
}

# Data Factory
resource "azurerm_data_factory" "adf" {
  name                = "adf-migration-${random_string.suffix.result}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  identity {
    type = "SystemAssigned"
  }
}
# Log Analytics
resource "azurerm_log_analytics_workspace" "log" {
  name                = "log-migration-${random_string.suffix.result}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Diagnostic Settings (Monitoring)
resource "azurerm_monitor_diagnostic_setting" "sql_metrics" {
  name                       = "sql-metrics"
  target_resource_id         = azurerm_mssql_server.sql_server.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id

  # Activer uniquement les métriques disponibles
  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert" "sql_errors" {
  name                = "sql-errors"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  data_source_id = azurerm_log_analytics_workspace.log.id
  description    = "SQL errors detected"
  severity       = 2
  enabled        = true

  query = <<QUERY
AzureDiagnostics
| where Category == "SQLSecurityAuditEvents"
| where action_name_s contains "FAILED"
QUERY

  frequency   = 5
  time_window = 5

  trigger {
    operator  = "GreaterThan"
    threshold = 0
  }

  action {
    action_group = [azurerm_monitor_action_group.alerts.id]
  }
}

resource "azurerm_monitor_diagnostic_setting" "sql_db_logs" {
  name                       = "sql_db_logs"
  target_resource_id = azurerm_mssql_database.db.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id

  enabled_log {
    category = "SQLInsights"
  }

  enabled_log {
    category = "AutomaticTuning"
  }

  enabled_log {
    category = "QueryStoreRuntimeStatistics"
  }

  metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "adf_logs" {
  name                       = "adf-logs"
  target_resource_id         = azurerm_data_factory.adf.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id

  enabled_log {
    category = "PipelineRuns"
  }

  enabled_log {
    category = "ActivityRuns"
  }

  enabled_log {
    category = "TriggerRuns"
  }

  metric {
    category = "AllMetrics"
  }
}

# Lifecycle policy for Storage
resource "azurerm_storage_management_policy" "lifecycle" {
  storage_account_id = azurerm_storage_account.storage.id

  rule {
    name    = "delete-old-data"
    enabled = true

    filters {
      blob_types = ["blockBlob"]
    }

    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = 30
      }
    }
  }
}

# Outputs
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "data_factory_name" {
  value = azurerm_data_factory.adf.name
}

resource "azurerm_monitor_action_group" "alerts" {
  name                = "alerts-group"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "alerts"

  email_receiver {
    name          = "admin"
    email_address = "ssh.cedric@gmail.com"
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert" "adf_failure_log" {
  name                = "adf-failed-pipeline-alert"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  description         = "Alert if any ADF pipeline fails"
  enabled             = true
  severity            = 3

  # Log Analytics Workspace cible
  data_source_id = azurerm_log_analytics_workspace.log.id

  # Requête Kusto
  query = <<KQL
ADFActivityRun
| where Status == "Failed"
| summarize count() by PipelineName, bin(TimeGenerated, 5m)
| where count_ > 0
KQL

  # Fenêtre temporelle
  time_window = 5

  # Fréquence d’exécution
  frequency = 5

  trigger {
    threshold = 0
    operator  = "GreaterThan"
  }

  action {
    action_group = [azurerm_monitor_action_group.alerts.id]
  }
}

resource "azurerm_monitor_metric_alert" "sql_dtu" {
  name                = "sql-high-dtu"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_mssql_server.sql_server.id]
  description         = "Alert if SQL Server CPU > 80%"
  severity            = 3
  enabled             = true

  criteria {
    metric_namespace = "Microsoft.Sql/servers"
    metric_name      = "dtu_used"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }

  action {
    action_group_id = azurerm_monitor_action_group.alerts.id
  }
}

resource "azurerm_monitor_metric_alert" "storage_capacity" {
  name                = "storage-capacity-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_storage_account.storage.id]
  description         = "Alert if storage usage > 80%"
  severity            = 3
  enabled             = true

  # Fenêtre d’évaluation et fréquence
  window_size = "PT1H"
  frequency   = "PT5M"

  criteria {
    metric_namespace = "Microsoft.Storage/storageAccounts"
    metric_name      = "UsedCapacity"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80000000000

  }

  action {
    action_group_id = azurerm_monitor_action_group.alerts.id

  }
}

