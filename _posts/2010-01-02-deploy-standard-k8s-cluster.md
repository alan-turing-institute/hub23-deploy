---
layout: page
share: false
title: "Deploy a standard Kubernetes Cluster"
---

This document walks through the steps required to deploy a standard Kubernetes cluster onto the Turing's Azure subscription.

We assume you have the following CLIs installed:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)

## Table of Contents

- [Setup](#setup)
- [Download the required secrets](#download-the-required-secrets)
- [Enable Network Policies](#enable-network-policies)
- [Create the Kubernetes cluster](#create-the-kubernetes-cluster)

---

## Setup

#### 1. Login to Azure

```bash
az login --username YOUR_TURING_EMAIL --output none
```

Login with your Turing account.

#### 2. Activate the Subscription

Hub23 has its own subscription and so we have to activate that.
To check which subscriptions you have access to, run the following:

```bash
az account list --refresh --output table
```

You should see `Turing-BinderHub` listed as an option.
If not, request access by opening a TopDesk ticket.

To activate the subscription, run the following:

```bash
az account set --subscription Turing-BinderHub
```

#### 3. Create a Resource Group

Azure groups related resources together by assigning them a Resource Group.
We need to create one for Hub23.

```bash
az group create --name Hub23 --location westeurope --output table
```

- `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
- `--location` sets the [region of data centres](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
- `--output table` prints the info in a human-readable format.

**NOTE:** If you have already followed the docs on creating a key vault, then this resource group should already exist and this step can be skipped.
{: .notice--info}

## Download the required secrets

We will require some info from the key vault in order to deploy the Kubernetes cluster and the BinderHub.

#### 1. Create a secrets folder

Create a folder in which to download the secrets so.
This will be git-ignored.

```bash
mkdir .secret
```

#### 2. Download the secrets

We will require the following secrets:

- Service Principal app ID and key
- public SSH key

They should be downloaded to files in the `.secret` folder so that they are git-ignored.

Download the Service Principal:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-appID \
    --file .secret/appID.txt
```

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-key \
    --file .secret/key.txt
```

Download the public SSH key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-Hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```

## Enable Network Policies

The BinderHub helm chart contains network policies designed to restrict access to pods and the JupyterHub.
However, the Kubernetes cluster will not be automatically configured to obey these network policies.
Therefore, we need create a virtual network (vnet) and sub network (subnet) with network policies enabled so that these pod traffic restrictions are obeyed.

See the following documentation: <https://docs.microsoft.com/en-us/azure/aks/use-network-policies#create-an-aks-cluster-and-enable-network-policy>

#### 1. Create a VNET

```bash
az network vnet create \
    --resource-group Hub23 \
    --name hub23-vnet \
    --address-prefixes 10.0.0.0/8 \
    --subnet-name hub23-subnet \
    --subnet-prefix 10.240.0.0/16
```

- `--address-prefixes`: IP address prefixes for the VNet;
- `--subnet-prefix`: IP address prefixes in CIDR format for the new subnet.

#### 2. Retrieve the VNet ID

This saves the VNet ID into a bash variable.

```bash
VNET_ID=$(
    az network vnet show \
    --resource-group Hub23 \
    --name hub23-vnet \
    --query id \
    --output tsv
)
```

#### 3. Assign the Contributor role to the Service Principal for accessing the VNet

```bash
az role assignment create \
    --assignee $(cat .secret/appID.txt) \
    --scope $VNET_ID \
    --role Contributor
```

**WARNING:** You must have Owner permissions on the subscription for this step to work.
{: .notice--warning}

#### 4. Retrieve the subnet ID

This will save the subnet ID to a bash variable.

```bash
SUBNET_ID=$(
    az network vnet subnet show \
    --resource-group Hub23 \
    --vnet-name hub23-vnet \
    --name hub23-subnet \
    --query id \
    --output tsv
)
```

## Create the Kubernetes cluster

#### 1. Create the AKS cluster

The following command will deploy a Kubernetes cluster into the Hub23 resource group.
This command has been known to take between 7 and 30 minutes to execute depending on resource availability in the location we set when creating the resource group.

```bash
az aks create --name hub23cluster \
    --resource-group Hub23 \
    --kubernetes-version 1.16.15 \
    --ssh-key-value .secret/ssh-key-hub23cluster.pub \
    --node-count 3
    --node-vm-size Standard_D2s_v3 \
    --service-principal $(cat .secret/appID.txt) \
    --client-secret $(cat .secret/key.txt) \
    --dns-service-ip 10.0.0.10 \
    --docker-bridge-address 172.17.0.1/16 \
    --network-plugin azure \
    --network-policy azure \
    --service-cidr 10.0.0.0/16 \
    --vnet-subnet-id $SUBNET_ID \
    --output table
```

- `--kubernetes-version`: It's recommended to use the most up-to-date version of Kubernetes.
- `--node-count` is the number of nodes to be deployed. 3 is recommended for a stable, scalable cluster.
- `--node-vm-size` denotes the type of virtual machine to be deployed. A list of Linux types can be found [here](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/).
- `--dns-service-ip`: An IP address assigned to the Kubernetes DNS service.
- `--docker-bridge-address`: A specific IP address and netmask for the Docker bridge, using standard CIDR notation.
- `--network-plugin`: The Kubernetes network plugin to use.
- `--network-policy`: The Kubernetes network policy to use.
- `--service-cidr`: A CIDR notation IP range from which to assign service cluster IPs.
- `--vnet-subnet-id`: The ID of a subnet in an existing VNet into which to deploy the cluster.

#### Delete local copies of the secret files

Once the Kubernetes cluster is deployed, you should delete the local copy of the Service Principal and public SSH key.

```bash
rm .secret/ssh-key-hub23cluster.pub
rm .secret/appID.txt
rm .secret/key.txt
```

#### 2. Get credentials for `kubectl`

We need to configure the local installation of the Kubernetes CLI to work with the version deployed onto the cluster, and do so with the following command.

```bash
az aks get-credentials \
    --name hub23cluster \
    --resource-group Hub23 \
    --output table
```

This command would need to be repeated when trying to manage the cluster from another computer or if you have been working with a different cluster.

#### 3. Check the cluster is fully functional

Output the status of the nodes.

```bash
kubectl get nodes
```

All three nodes should have `STATUS` as `Ready`.
