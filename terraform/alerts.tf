resource "azurerm_monitor_action_group" "email" {
  name                = "alert-alert"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "alert"

  email_receiver {
    name          = "admin"
    email_address = "ssh.cedric@gmail.com"
  }
}

resource "azurerm_monitor_metric_alert" "dlq_alert" {
  name                = "dlq-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_servicebus_namespace.sb.id]

  criteria {
    metric_namespace = "Microsoft.ServiceBus/namespaces"
    metric_name      = "DeadletteredMessages"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 0
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }

  frequency   = "PT1M"
  window_size = "PT5M"
}
