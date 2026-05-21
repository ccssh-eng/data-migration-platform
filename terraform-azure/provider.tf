terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstatexxxx"
    container_name       = "tfstate"
    key                  = "data-migration-platform.tfstate"
  }
}
