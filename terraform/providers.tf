terraform {
    required_version = ">= 0.13"

    required_providers {
        azurerm = {
            source  = "hashicorp/azurerm"
            version = "2.25.0"
        }
        kubernetes = {
            source  = "hashicorp/kubernetes"
            version = "1.13.2"
        }
    }
}
