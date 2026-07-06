# ----------------------------------------
# ADF INSTANCE
# ----------------------------------------
resource "azurerm_data_factory" "adf" {
  name                = "adf-data-migration-0cue2d"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  identity {
    type = "SystemAssigned"
  }
}

# ----------------------------------------
# LINKED SERVICE — Azure SQL (source)
# ----------------------------------------
resource "azurerm_data_factory_linked_service_azure_sql_database" "sql_source" {
  name            = "ls-sql-source"
  data_factory_id = azurerm_data_factory.adf.id

  connection_string = "integrated security=False;encrypt=True;connection timeout=30;data source=sql0cue2d.database.windows.net;initial catalog=migration-db;user id=sqladmin@sshcedricgmail.onmicrosoft.com"
}

# ----------------------------------------
# LINKED SERVICE — Blob Storage (destination)
# ----------------------------------------
resource "azurerm_data_factory_linked_service_azure_blob_storage" "blob_dest" {
  name                 = "ls-blob-destination"
  data_factory_id      = azurerm_data_factory.adf.id
  use_managed_identity = true
  service_endpoint     = "https://stdatamigration0cue2d.blob.core.windows.net"
}

# ---------------------------------------------------------
# DATASET — SQL Source (table customers) (version générique)
# ---------------------------------------------------------
resource "azurerm_data_factory_custom_dataset" "ds_sql_source" {
  name            = "ds-sql-customers"
  data_factory_id = azurerm_data_factory.adf.id
  type            = "AzureSqlTable"

  linked_service {
    name = azurerm_data_factory_linked_service_azure_sql_database.sql_source.name
  }

  type_properties_json = jsonencode({
    schema    = "dbo"
    table     = "customers"
  })

  schema_json = jsonencode([
    { name = "id",          type = "Int32"    },
    { name = "name",        type = "String"   },
    { name = "email",       type = "String"   },
    { name = "signup_date", type = "DateTime" },
    { name = "country",     type = "String"   }
  ])
}

# ----------------------------------------
# DATASET — CSV Destination (Blob)
# ----------------------------------------
resource "azurerm_data_factory_dataset_delimited_text" "ds_csv_dest" {
  name                = "ds-csv-customers"
  data_factory_id     = azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.blob_dest.name

  azure_blob_storage_location {
    container = "raw"
    filename  = "customers_legacy.csv"
  }

  column_delimiter    = ","
  row_delimiter       = "\n"
  first_row_as_header = true
  encoding            = "UTF-8"
}

# ----------------------------------------
# PIPELINE — Copy Activity SQL → CSV
# ----------------------------------------
resource "azurerm_data_factory_pipeline" "pipeline_export" {
  name            = "pipeline-export-customers"
  data_factory_id = azurerm_data_factory.adf.id

  activities_json = jsonencode([
    {
      name = "CopyCustomers"
      type = "Copy"
      inputs = [
        {
          referenceName = azurerm_data_factory_custom_dataset.ds_sql_source.name
          type          = "DatasetReference"
        }
      ]
      outputs = [
        {
          referenceName = azurerm_data_factory_dataset_delimited_text.ds_csv_dest.name
          type          = "DatasetReference"
        }
      ]
      typeProperties = {
        source = {
          type           = "AzureSqlSource"
          sqlReaderQuery = "SELECT id, name, email, signup_date, country FROM customers"
        }
        sink = {
          type          = "DelimitedTextSink"
          storeSettings = { type = "AzureBlobStorageWriteSettings" }
          formatSettings = {
            type          = "DelimitedTextWriteSettings"
            quoteAllText  = true
            fileExtension = ".csv"
          }
        }
        enableStaging = false
      }
    }
  ])
}

# ----------------------------------------
# TRIGGER — Cron quotidien à 02h00 UTC
# ----------------------------------------
resource "azurerm_data_factory_trigger_schedule" "trigger_daily" {
  name            = "trigger-daily-02h00"
  data_factory_id = azurerm_data_factory.adf.id
  pipeline_name   = azurerm_data_factory_pipeline.pipeline_export.name

  interval   = 1
  frequency  = "Day"
  start_time = "2026-07-02T02:00:00Z"  # ← date future

  activated = true
}

# ----------------------------------------
# ROLE — ADF blob contributor
# ----------------------------------------
resource "azurerm_role_assignment" "adf_blob_contributor" {
  scope                = data.azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}

# ----------------------------------------
# ROLE — ADF SQL contributor
# ----------------------------------------
resource "azurerm_role_assignment" "adf_sql_contributor" {
  scope                = "/subscriptions/6684f3b2-db8e-4118-9d74-3c7d7b6e055f/resourceGroups/rg-data-migration/providers/Microsoft.Sql/servers/sql0cue2d"
  role_definition_name = "SQL DB Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}

