terraform {
    required_version = ">= 0.13"

    required_providers {
        azurerm = {
            source  = "hashicorp/azurerm"
            version = "2.25.0"
        }
        external = {
            source  = "hashicorp/external"
            version = "1.2.0"
        }
    }
}

provider "azurerm" {
    version = "~> 2.0"
    features {}
}

provider "external" {
  version = "~> 1.2"
}

# Set Variables
variable "kubernetes_version" {
    default     = "1.18.10"
    description = "The Kubernetes orchestrator version to install"
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
    sku                 = "Standard"
}

# DNS Zone
resource "azurerm_dns_zone" "dns" {
    name                = "hub23.turing.ac.uk"
    resource_group_name = azurerm_resource_group.rg.name
}

# A Records in DNS Zone
resource "azurerm_dns_a_record" "binder_a_rec" {
    name                = "binder"
    zone_name           = azurerm_dns_zone.dns.name
    resource_group_name = azurerm_resource_group.rg.name
    ttl                 = 300
    target_resource_id  = azurerm_public_ip.ipaddr.id
}

resource "azurerm_dns_a_record" "hub_a_rec" {
    name                = "hub"
    zone_name           = azurerm_dns_zone.dns.name
    resource_group_name = azurerm_resource_group.rg.name
    ttl                 = 300
    target_resource_id  = azurerm_public_ip.ipaddr.id
}

# IP Address
resource "azurerm_public_ip" "ipaddr" {
    name                = "kubernetes-public-ip"
    resource_group_name = azurerm_kubernetes_cluster.k8s.node_resource_group
    location            = azurerm_resource_group.rg.location
    allocation_method   = "Dynamic"

    tags = {
        kubernetes-cluster-name = "kubernetes"
        service                 = "hub23/hub23-nginx-ingress-controller"
    }
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

# Kubernetes Cluster
resource "azurerm_kubernetes_cluster" "k8s" {
    name                = "hub23cluster"
    kubernetes_version  = var.kubernetes_version
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    dns_prefix          = "hub23clust-Hub23-ecaf04"
    node_resource_group = "MC_${azurerm_resource_group.rg.name}_hub23cluster_${azurerm_resource_group.rg.location}"

    default_node_pool {
        name                  = "core"
        enable_auto_scaling   = true
        node_count            = 1
        min_count             = 1
        max_count             = 2
        os_disk_size_gb       = 128
        orchestrator_version  = var.kubernetes_version
        vm_size               = "Standard_D2s_v3"
        vnet_subnet_id        = azurerm_subnet.subnet.id
        node_labels           = {"hub.jupyter.org/node-purpose" = "core"}
    }

    linux_profile {
        admin_username = "azureuser"

        ssh_key {
            key_data = local.sshKey
        }
    }

    network_profile {
        network_plugin     = "azure"
        network_policy     = "azure"
        dns_service_ip     = "10.0.0.10"
        docker_bridge_cidr = "172.17.0.1/16"
        service_cidr       = "10.0.0.0/16"
    }

    role_based_access_control {
        enabled = true
    }

    service_principal {
        client_id     = local.appId
        client_secret = local.appKey
    }
}

# Add second nodepool to Kubernetes cluster
resource "azurerm_kubernetes_cluster_node_pool" "k8s_np" {
    name                  = "user"
    kubernetes_cluster_id = azurerm_kubernetes_cluster.k8s.id
    vm_size               = "Standard_D2s_v3"
    enable_auto_scaling   = true
    node_labels           = {"hub.jupyter.org/node-purpose" = "user"}
    orchestrator_version  = var.kubernetes_version
    os_disk_size_gb       = 128
    vnet_subnet_id        = azurerm_subnet.subnet.id
    node_count            = 2
    min_count             = 2
    max_count             = 6
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

# Extract secrets from the vault
data "external" "appId" {
    program = ["az", "keyvault", "secret", "show", "--vault-name", azurerm_key_vault.keyvault.name, "--name", "SP-appId", "--query", "{value: value}"]
}

data "external" "appKey" {
    program = ["az", "keyvault", "secret", "show", "--vault-name", azurerm_key_vault.keyvault.name, "--name", "SP-key", "--query", "{value: value}"]
}

data "external" "sshKey" {
    program = ["az", "keyvault", "secret", "show", "--vault-name", azurerm_key_vault.keyvault.name, "--name", "ssh-key-Hub23cluster-public", "--query", "{value: value}"]
}

locals {
    appId = data.external.appId.result.value
    appKey = data.external.appKey.result.value
    sshKey = data.external.sshKey.result.value
}

# # Role assignments
# resource "azurerm_role_assignment" "sp-aks-acrpush" {
#     scope                = azurerm_container_registry.acr.id
#     role_definition_name = "AcrPush"
#     principal_id         = local.appId
# }

# resource "azurerm_role_assignment" "sp-vnet-contributor" {
#     scope                = azurerm_virtual_network.vnet.id
#     role_definition_name = "Contributor"
#     principal_id         = local.appId
# }
