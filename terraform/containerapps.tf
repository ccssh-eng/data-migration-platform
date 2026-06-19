resource "azurerm_container_app_environment" "env" {
  name                       = "env-data-migration"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

resource "azurerm_container_app" "worker" {
  name                         = "worker-data-migration"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id

  template {
    container {
      name   = "worker"
      image  = "acr0cue2d.azurecr.io/data-worker:latest"
      cpu    = 1
      memory = "2Gi"
    }
  }
}

resource "azurerm_container_app" "dlq" {
  name                         = "dlq-monitor-data-migration"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id

  template {
    container {
      name   = "dlq"
      image  = "acr0cue2d.azurecr.io/dlq-monitor:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }
}
