terraform {
}
  # 5. Run: terraform init
  # 4. Update the values with your actual resource details
  # 3. Uncomment the backend block above
  # 2. Create a container named "tfstate" in the storage account
  # 1. Create the resource group and storage account in Azure
  # To use remote state:

  # }
  #   key                  = "fraud-detection/terraform.tfstate"
  #   container_name       = "tfstate"
  #   storage_account_name = "tfstateaccount"
  #   resource_group_name  = "rg-terraform-state"
  # backend "azurerm" {
  #
  # This ensures team members use the same state and prevents conflicts
  # Uncomment and configure to use Azure Storage Account for remote state management
  # Configure remote state storage

