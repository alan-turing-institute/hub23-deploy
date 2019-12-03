---
layout: page
share: false
title: "Creating an Azure Key Vault for Hub23"
---

This document walks through the creation of a key vault for the Turing BinderHub (Hub23) and how to save and extract secrets from it.

It assumes you have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) installed.

Table of Contents:

- [Setup and Create the Key Vault](#setup-and-create-the-key-vault)
- [Adding secrets to the Key Vault](#adding-secrets-to-the-key-vault)
- [Downloading the secrets](#downloading-the-secrets)
  - [Saving secrets to files](#saving-secrets-to-files)
  - [Saving secrets to bash variables](#saving-secrets-to-bash-variables)
- [Service Principal](#service-principal)

---

## Setup and Create the Key Vault

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

Azure groups related resources together by assigning them to a Resource Group.
We need to create one for Hub23.

```bash
az group create --name Hub23 --location westeurope --output table
```

- `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
- `--location` sets the [region of data centres](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
- `--output table` prints the info in a human-readable format.

**NOTE:** If the resource group already exists, this step can be skipped.
Test if the resource group exists by running the following: ```az group exists --name Hub23```
{: .notice--info}

#### 4. Create the key vault

**Key vault names must be lower case and/or numerical and may only include hyphens (`-`), no underscores (`_`) or other non-alphanumeric characters.**
**They must also be unique.**

```bash
az keyvault create --name hub23-keyvault --resource-group Hub23
```

## Adding secrets to the Key Vault

Hub23 requires some secrets, passwords, tokens etc. for functionality.

- SSH keys for accessing the Kubernetes cluster
- API and secret token

#### 1. Create a secrets folder

Create a folder to save secret files to. This will be git-ignored by this repo.

```bash
mkdir .secret/
```

#### 2. Generate the SSH keys

The following command will generate a pair of ssh keys, one private and one public (appended with `.pub`), and save them to files in the `.secret/` folder.

```bash
ssh-keygen --file .secret/ssh-key-hub23cluster
```

We have appended the file names with `hub23cluster` which is the cluster name we will assign to the Kubernetes cluster on deployment.
The name follows the same rule as the key vault.

#### 3. Add the SSH keys to the vault

Add the private key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name ssh-key-Hub23cluster-private \
    --file .secret/ssh-key-hub23cluster
```

Add the public key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name ssh-key-Hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```

**Now delete the local copies of the SSH keys.**

```bash
rm .secret/ssh-key-hub23cluster*
```

#### 4. Add API and secret tokens to the vault

We can create the tokens and save them to the vault in one step using the `--value` argument.

Add the API token:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name apiToken \
    --value $(openssl rand -hex 32)
```

Add the secret token:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name secretToken \
    --value $(openssl rand -hex 32)
```

## Downloading the secrets

### Saving secrets to files

We can download the secrets and save them to files like so.
They should be downloaded into the `.secret/` folder so that they are git-ignored.
We will need certain secrets in order to create the `config.yaml` and `secret.yaml` files to deploy and upgrade Hub23.

#### 1. Download the SSH keys

Download the private key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-Hub23cluster-private \
    --file .secret/ssh-key-hub23cluster
```

Download the public key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-Hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```

#### 2. Download the API and secret tokens

Download the API token:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name apiToken \
    --file .secret/apiToken.txt
```

Download the secret token:

```bash
az keyvault secret download \
    --vault-name hub3-keyvault \
    --name secretToken \
    --file .secret/secretToken.txt
```

### Saving secrets to bash variables

You may not wish to download the secrets to a file but rather save them to a bash variable instead.
This can be achieved like so, using the API token as an example case:

```bash
API_TOKEN=$(
    az keyvault secret show
    --vault-name hub23-keyvault
    --name apiToken
    --query value
    --output tsv
)
```

Here, `tsv` stands for 'Tab Separated Variable'.

## Service Principal

When deploying a Kubernetes cluster onto Azure, a Service Principal is required.
A Service Principal is a protocol, consisting of an app ID and a key, that grants the cluster permissions to act on behalf of both the user and itself.
REG members presently don't have permissions to create Service Principals and so IT Services create them on our behalf via a TopDesk request.
I (@sgibson91) have saved the Service Principal to the key vault for safe-keeping.
The following steps document how I did it and how one would download the Service Principal again.

Add the app ID:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name SP-appID \
    --value <redacted>
```

Add the key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name SP-key \
    --value <redacted>
```

Download the app ID and save to a file:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-appID \
    --file .secret/appID.txt
```

Download the key and save to a file:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-secret \
    --file .secret/key.txt
```
