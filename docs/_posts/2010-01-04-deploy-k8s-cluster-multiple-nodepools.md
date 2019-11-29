---
layout: page
share: false
title: "Deploy a Kubernetes Cluster with Multiple Nodepools"
---

This document walks through the steps required to deploy a Kubernetes cluster with multiple nodepools onto the Turing's Azure subscription.

We assume you have the following CLIs installed:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)

Table of Contents:

- [Setup](#setup)
- [Download the required secrets](#download-the-required-secrets)
- [Setup for Multiple Nodepools](#setup-for-multiple-nodepools)
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
az account set --subcription Turing-BinderHub
```

#### 3. Create a Resource Group

Azure groups related resources together by assigning them a Resource Group.
We need to create one for Hub23.

```bash
az group create --name Hub23 --location westeurope --output table
```

- `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
- `--location` sets the [data centre](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
- `--output table` prints the info in a human-readable format.

**N.B.:** If you have already followed the docs on creating a key vault, then this resource group should already exist and this step can be skipped.

## Download the required secrets

We will require some info from the key vault in order to deploy the Kubernetes cluster and the BinderHub.

#### 1. Create a secrets folder

Create a folder in which to download the secrets to.
This will be git-ignored.

```mkdir
mkdir .secret
```

#### 2. Download the secrets

We will require the following secrets:

- Service Principal app ID and key
- public SSH key
- API and secret tokens

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

Download the API and secret tokens:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name apiToken \
    --file .secret/apiToken.txt
```

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name secretToken \
    --file .secret/secretToken.txt
```

## Setup for Multiple Nodepools

See the following docs:

- <https://docs.microsoft.com/en-gb/azure/aks/use-multiple-node-pools>
- <https://docs.microsoft.com/en-us/cli/azure/ext/aks-preview/aks/nodepool?view=azure-cli-latest>

#### 1. Install aks-preview CLI extension

```bash
az extension add --name aks-preview
```

#### 2. Register the Multiple Nodepool feature

```bash
az feature register \
    --name MultiAgentpoolPreview \
    --namespace Microsoft.ContainerService
```

This can take a long time to register.
Check on the status with the following command:

```bash
az feature show \
    --name MultiAgentpoolPreview \
    --namespace Microsoft.ContainerService \
    --output table
```

#### 3. Register with the provider

When the previous feature has registered, we now need to register it with the provider.

```bash
az provider register --namespace Microsoft.ContainerService
```

## Create the Kubernetes cluster

**NOTE:** These commands can also be used in conjunction with those in ["Deploy an Autoscaling Kubernetes Cluster"]({% post_url 2010-01-03-deploy-autoscaling-k8s-cluster %}) to create autoscaling nodepools.

#### 1. Create the AKS cluster

The following command will deploy a Kubernetes cluster into the Hub23 resource group.
This command has been known to take between 7 and 30 minutes to execute depending on resource availability in the location we set when creating the resource group.

```bash
az aks create \
    --resource-group Hub23 \
    --name hub23cluster \
    --kubernetes-version 1.14.6 \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --nodepool-name default \
    --service-principal $(cat .secret/appID.txt) \
    --client-secret $(cat .secret/key.txt) \
    --ssh-key-value .secret/ssh-key-hub23cluster.pub \
    ---output table
```

- `--node-count` is the number of nodes to be deployed. 3 is recommended for a stable, scalable cluster.
- `--kubernetes-version`: It's recommended to use the most up-to-date version of Kubernetes.
- `--nodepool-name` sets the name of the first pool.

**NOTE:** The default nodepool _cannot_ be deleted.

#### Delete local copies of the secret files

Once the Kubernetes cluster is deployed, you should delete the local copy of the Service Principal and public SSH key.

```bash
rm .secret/ssh-key-hub23cluster.pub
rm .secret/appID.txt
rm .secret/key.txt
```

#### 2. Add another node

To add another nodepool to the cluster, run the following (e.g. adding a `core` nodepool):

```bash
az aks nodepool add \
    --cluster-name hub23cluster \
    --name core \
    --resource-group Hub23 \
    --kubernetes-version 1.14.6 \
    --node-count 1 \
    --node-vm-size Standard_D2s_v3
```

**NOTE:** The flags to enable autoscaling can also be used here.

The same command can be run to create a `user` nodepool.
I would recommend a `--node-count 2`.

#### Scaling the `default` nodepool back

I would recommend scaling the `default` nodepool down to 1 node as we will most likely use node affinities to preferentially assign core pods to the core pool and user pods to the user pool (see ["Optimizing the JupyterHub for Autoscaling"]({% post_url 2010-01-13-optimising-autoscaling %})).

```bash
az aks nodepool scale \
    --cluster-name hub23cluster \
    --name default \
    --resource-group Hub23 \
    --node-count 1
```

#### 3. Get credentials for `kubectl`

We need to configure the local installation of the Kubernetes CLI to work with the version deployed onto the cluster, and do so with the following command.

```bash
az aks get-credentials \
    --name hub23cluster \
    --resource-group Hub23
```

This command would need to be repeated when trying to manage the cluster from another computer or if you have been working with a different cluster.

#### 4. Check the cluster is fully functional

Output the status of the nodes.

```bash
kubectl get nodes
```

All nodes should have `STATUS` as `Ready`.
