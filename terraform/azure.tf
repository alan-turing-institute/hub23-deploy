provider "azurerm" {
    version = "~> 2.0"
    features {}
}

# Resource Group
resource "azurerm_resource_group" "rg" {
    name     = "Hub23"
    location = "westeurope"
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
    name = "hub23-subnet"
    resource_group_name = azurerm_resource_group.rg.name
    virtual_network_name = azurerm_virtual_network.vnet.name
    address_prefixes = ["10.240.0.0/16"]
}
