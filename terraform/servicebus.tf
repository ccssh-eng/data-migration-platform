resource "azurerm_servicebus_namespace" "sb" {
  name                = "sb-data-migration-tgt1"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
}

resource "azurerm_servicebus_topic" "topic" {
  name         = "etl-topic"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_subscription" "sub" {
  name     = "etl-sub"
  topic_id = azurerm_servicebus_topic.topic.id
  max_delivery_count = 10
}

