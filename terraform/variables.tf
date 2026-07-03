variable "resource_group_name" {
  default = "rg-data-migration"
}

variable "location" {
  default = "francecentral"
}

variable "acr_name" {
  default = "acr0cue2d"
}

variable "servicebus_namespace" {
  default = "sb-data-migration-tgt1"
}

variable "servicebus_topic" {
  default = "etl-topic"
}

variable "servicebus_subscription" {
  default = "etl-sub"
}

variable "servicebus_connection_string" {
  description = "Connection string Service Bus pour le scaler KEDA"
  type        = string
  sensitive   = true
}

variable "sql_server" {
  description = "Nom du serveur SQL Azure ex: monserveur.database.windows.net"
  type        = string
}

variable "sql_database" {
  description = "Nom de la base de données SQL"
  type        = string
}

variable "acr_username" {
  description = "Username ACR admin"
  type        = string
}

variable "acr_password" {
  description = "Password ACR admin"
  type        = string
  sensitive   = true
}

