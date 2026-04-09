variable "resource_group_name" {
  description = "Nom du resource group"
  type        = string
  default     = "rg-data-migration"
}

variable "location" {
  description = "Région Azure"
  type        = string
  default     = "France Central"
}

variable "sql_admin_user" {
  description = "Admin SQL"
  type        = string
}

variable "sql_admin_password" {
  description = "Mot de passe SQL"
  type        = string
  sensitive   = true
}
