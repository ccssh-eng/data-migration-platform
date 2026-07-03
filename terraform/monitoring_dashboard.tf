resource "azurerm_portal_dashboard" "main" {
  name                = "dashboard-data-migration"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  tags = {
    "hidden-title" = "dashboard-data-migration"
  }

  dashboard_properties = jsonencode({
    lenses = {
      "0" = {                         
        order = 0
        parts = {
          # Worker CPU
          "0" = {                     
            position = { x = 0, y = 0, colSpan = 6, rowSpan = 4 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MonitorChartPart"
              inputs = [{
                name = "options"
                value = {
                  chart = {
                    title = "Worker CPU"
                    metrics = [{
                      aggregationType  = 4
                      name             = "UsageNanoCores"
                      resourceMetadata = { id = azurerm_container_app.worker.id }
                    }]
                  }
                }
              }]
            }
          },
          # Worker Memory
          "1" = {
            position = { x = 6, y = 0, colSpan = 6, rowSpan = 4 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MonitorChartPart"
              inputs = [{
                name = "options"
                value = {
                  chart = {
                    title = "Worker Memory"
                    metrics = [{
                      aggregationType  = 4
                      name             = "WorkingSetBytes"
                      resourceMetadata = { id = azurerm_container_app.worker.id }
                    }]
                  }
                }
              }]
            }
          },
          # Replicas & Restart Count
          "2" = {
            position = { x = 0, y = 4, colSpan = 6, rowSpan = 4 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MonitorChartPart"
              inputs = [{
                name = "options"
                value = {
                  chart = {
                    title = "Replicas & Restart Count"
                    metrics = [
                      {
                        aggregationType  = 4
                        name             = "Replicas"
                        resourceMetadata = { id = azurerm_container_app.worker.id }
                      },
                      {
                        aggregationType  = 1
                        name             = "RestartCount"
                        resourceMetadata = { id = azurerm_container_app.worker.id }
                      }
                    ]
                  }
                }
              }]
            }
          },
          # Service Bus — Active & DLQ
          "3" = {
            position = { x = 6, y = 4, colSpan = 6, rowSpan = 4 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MonitorChartPart"
              inputs = [{
                name = "options"
                value = {
                  chart = {
                    title = "Service Bus — Active & DLQ"
                    metrics = [
                      {
                        aggregationType  = 4
                        name             = "ActiveMessages"
                        resourceMetadata = { id = azurerm_servicebus_namespace.sb.id }
                      },
                      {
                        aggregationType  = 4
                        name             = "DeadletteredMessages"
                        resourceMetadata = { id = azurerm_servicebus_namespace.sb.id }
                      }
                    ]
                  }
                }
              }]
            }
          }
        }
      }
    }
    metadata = { model = {} }
  })
}

