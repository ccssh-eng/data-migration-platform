terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }

  # Backend distant pour GitHub Actions
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstatecue2d"
    container_name       = "tfstate"
    key                  = "data-migration-platform.tfstate"
  }
}

provider "azurerm" {
  features {}
}


