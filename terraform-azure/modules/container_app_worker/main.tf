resource "azurerm_container_app" "worker" { 
name = "worker-${var.project_name}" 
container_app_environment_id = var.environment_id 
resource_group_name = var.resource_group_name 
revision_mode = "Single" 

identity { 
type = "UserAssigned" 
identity_ids = [var.identity_id] 
} 

registry { 
server = var.acr_login_server 
identity = var.identity_id 
} 

secret {
 name = "sb-connection" 
value = var.servicebus_connection_string 
} 
template { 
  container { 
    name = "worker" image = "${var.acr_login_server}/data-worker:v7" 
    cpu = 1 
    memory = "2Gi" 
    
    env { 
      name = "SERVICEBUS_NAMESPACE" 
      value = var.servicebus_namespace_fqdn 
   }

   env { 
      name = "SQL_SERVER" 
      value = var.sql_server_fqdn 
   } 
   env { 
      name = "SQL_DATABASE" 
      value = var.sql_database_name 
   } 
   env { 
      name = "MANAGED_IDENTITY_CLIENT_ID" 
      value = var.identity_client_id 
    } 
} 
min_replicas = 0 
max_replicas = 1 
custom_scale_rule { 
   name = "servicebus-scaler" 
   custom_rule_type = "azure-servicebus" 
   metadata = {
       topicName = "etl-topic" 
       subscriptionName = "etl-sub" 
       namespace = "sb-data-migration-tgt1" 
       messageCount = "1" 
  } 
  authentication { 
     secret_name = "sb-connection" 
     trigger_parameter = "connection"
  } 
} 
} 
}
