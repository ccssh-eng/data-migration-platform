# ACTION GROUPS

resource "azurerm_monitor_action_group" "email" {
  name                = "alert-alert"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "alert"

  email_receiver {
    name          = "admin"
    email_address = "ssh.cedric@gmail.com"
  }
}

resource "azurerm_monitor_action_group" "alerts_group" {
  name                = "alerts-group"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "alerts"

  email_receiver {
    name          = "admin"
    email_address = "ssh.cedric@gmail.com"
  }
}

resource "azurerm_monitor_action_group" "ag_data_migration" {
  name                = "ag-data-migration"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "DLQAlert"
  location            = "germanywestcentral"

  email_receiver {
    name          = "admin"
    email_address = "ssh.cedric@gmail.com"
  }
}

# ALERTE 1 — DLQ > 0

resource "azurerm_monitor_metric_alert" "dlq_alert" {
  name                = "dlq-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_servicebus_namespace.sb.id]
  description         = "Messages en dead-letter détectés"
  severity            = 2  # Warning
  enabled             = false    # desactivé temporairement

  criteria {
    metric_namespace = "Microsoft.ServiceBus/namespaces"
    metric_name      = "DeadletteredMessages"
    aggregation      = "Maximum"
    operator         = "GreaterThan"
    threshold        = 0
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT15M"   # prolongé à 15 au lieu de 5
}

# ALERTE 2 — Active Messages bloqués > 10

resource "azurerm_monitor_metric_alert" "active_messages_alert" {
  name                = "active-messages-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_servicebus_namespace.sb.id]
  description         = "Trop de messages actifs en attente"
  severity            = 2  # Warning
  enabled             = false

  criteria {
    metric_namespace = "Microsoft.ServiceBus/namespaces"
    metric_name      = "ActiveMessages"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 10
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT15M"
}

# ALERTE 3 — Worker Restart Count > 3

resource "azurerm_monitor_metric_alert" "worker_restart_alert" {
  name                = "worker-restart-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_container_app.worker.id]
  description         = "Le worker redémarre trop souvent"
  severity            = 1  # Critical
  enabled             = false

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "RestartCount"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 3
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT15M"
}

# ALERTE 4 — Worker CPU > 80%

resource "azurerm_monitor_metric_alert" "worker_cpu_alert" {
  name                = "worker-cpu-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_container_app.worker.id]
  description         = "CPU du worker trop élevé"
  severity            = 2  # Warning
  enabled             = false

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "UsageNanoCores"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 800000000  # 80% de 1 core = 800m nanocores
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT15M"
}

# ALERTE 5 — Worker Memory > 80%
resource "azurerm_monitor_metric_alert" "worker_memory_alert" {
  name                = "worker-memory-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_container_app.worker.id]
  description         = "Mémoire du worker trop élevée"
  severity            = 2  # Warning
  enabled             = false

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "WorkingSetBytes"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 1717986918  # 80% de 2Gi = 1.6Gi en bytes
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT15M"
}

