(content:key-vault:create)=
# Setup and Create the Key Vault

## Login to Azure

```bash
az login --username YOUR_TURING_EMAIL --output none
```

Login with your Turing account.

## Activate the Subscription

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

## Create a Resource Group

Azure groups related resources together by assigning them to a Resource Group.
We need to create one for Hub23.

```bash
az group create --name Hub23 --location westeurope --output table
```

- `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
- `--location` sets the [region of data centres](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
- `--output table` prints the info in a human-readable format.

```{note}
If the resource group already exists, this step can be skipped.
Test if the resource group exists by running the following: `az group exists --name Hub23`
```

## Create the key vault

```{note}
Key vault names must be lower case and/or numerical and may only include hyphens (`-`), no underscores (`_`) or other non-alphanumeric characters. They must also be unique.
```

```bash
az keyvault create --name hub23-keyvault --resource-group Hub23
```
