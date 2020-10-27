provider "azurerm" {
    version = "~> 2.0"
    features {}
}

# Get info about currently activated subscription
data "azurerm_subscription" "current" {}

# Resource Group
resource "azurerm_resource_group" "rg" {
    name     = "Hub23"
    location = "westeurope"
}

# Container Registry
resource "azurerm_container_registry" "acr" {
    name                = "hub23registry"
    resource_group_name = azurerm_resource_group.rg.name
    location            = azurerm_resource_group.rg.location
    sku                 = "Basic"
    admin_enabled       = true
}

# Key Vault
resource "azurerm_key_vault" "keyvault" {
    name                       = "hub23-keyvault"
    location                   = azurerm_resource_group.rg.location
    resource_group_name        = azurerm_resource_group.rg.name
    sku_name                   = "standard"
    tenant_id                  = data.azurerm_subscription.current.tenant_id
    soft_delete_enabled        = true
    soft_delete_retention_days = 90
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
    name                = "hub23-vnet"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    address_space       = ["10.0.0.0/8"]
}

# Virtual Network Subnet
resource "azurerm_subnet" "subnet" {
    name                 = "hub23-subnet"
    resource_group_name  = azurerm_resource_group.rg.name
    virtual_network_name = azurerm_virtual_network.vnet.name
    address_prefixes     = ["10.240.0.0/16"]
}

# Define Outputs
output "resource_group_name" {
    value = azurerm_resource_group.rg.name
}

output "location" {
    value = azurerm_resource_group.rg.location
}

output "acr_login_server" {
    value = azurerm_container_registry.acr.login_server
}

output "key_vault_name" {
    value = azurerm_key_vault.keyvault.name
}
