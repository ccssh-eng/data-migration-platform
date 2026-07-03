# ENVIRONMENT
resource "azurerm_container_app_environment" "env" {
  name                       = "env-data-migration"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

# WORKER
resource "azurerm_container_app" "worker" {
  name                         = "worker-data-migration"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name  = "acr-password"
    value = var.acr_password
  }

  secret {
    name  = "servicebus-connection"  
    value = var.servicebus_connection_string 
  }

  registry {
    server   = "${var.acr_name}.azurecr.io"
    username             = var.acr_username
    password_secret_name = "acr-password"
  }

  template {
    min_replicas = 0
    max_replicas = 5

    container {
      name   = "worker"
      image  = "${var.acr_name}.azurecr.io/data-worker:latest"
      cpu    = 1
      memory = "2Gi"

      env {
        name  = "SERVICEBUS_NAMESPACE"
        value = "${var.servicebus_namespace}.servicebus.windows.net"
      }
      env {
        name  = "TOPIC_NAME"
        value = var.servicebus_topic
      }
      env {
        name  = "SUBSCRIPTION_NAME"
        value = var.servicebus_subscription
      }
      env {
        name  = "SQL_SERVER"
        value = var.sql_server
      }
      env {
        name  = "SQL_DATABASE"
        value = var.sql_database
      }
    }

    custom_scale_rule {
      name             = "servicebus-scaler"
      custom_rule_type = "azure-servicebus"

      metadata = {
        namespace        = var.servicebus_namespace
        topicName        = var.servicebus_topic
        subscriptionName = var.servicebus_subscription
        messageCount     = "20"
      }

      authentication {
        secret_name       = "servicebus-connection"
        trigger_parameter = "connection"
      }
    }
  }
}

resource "azurerm_role_assignment" "worker_servicebus_receiver" {
  scope                = "/subscriptions/6684f3b2-db8e-4118-9d74-3c7d7b6e055f/resourceGroups/rg-data-migration/providers/Microsoft.ServiceBus/namespaces/sb-data-migration-tgt1"
  role_definition_name = "Azure Service Bus Data Receiver"
  principal_id         = azurerm_container_app.worker.identity[0].principal_id
}

# DLQ MONITOR
resource "azurerm_container_app" "dlq" {
  name                         = "dlq-monitor-data-migration"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name  = "acr-password"
    value = var.acr_password
  }

  registry {
    server               = "${var.acr_name}.azurecr.io"
    username             = var.acr_username
    password_secret_name = "acr-password"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "dlq"
      image  = "${var.acr_name}.azurecr.io/dlq-monitor:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "SERVICEBUS_NAMESPACE"
        value = "${var.servicebus_namespace}.servicebus.windows.net"
      }
      env {
        name  = "TOPIC_NAME"
        value = var.servicebus_topic
      }
      env {
        name  = "SUBSCRIPTION_NAME"
        value = var.servicebus_subscription
      }
    }
  }
}

# Récupérer l'ACR existant
data "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
}

# Rôle AcrPull pour le worker
resource "azurerm_role_assignment" "worker_acr_pull" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.worker.identity[0].principal_id
}

# Rôle AcrPull pour le dlq monitor
resource "azurerm_role_assignment" "dlq_acr_pull" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.dlq.identity[0].principal_id
}

# Data source
data "azurerm_storage_account" "storage" {
  name                = "stdatamigration0cue2d"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_role_assignment" "worker_blob_reader" {
  scope                = data.azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_container_app.worker.identity[0].principal_id
}

