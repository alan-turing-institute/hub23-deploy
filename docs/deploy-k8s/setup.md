(content:k8s:setup)=
# Setup

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

You should see `turingmybinder` listed as an option.
If not, request access by opening a TopDesk ticket.

To activate the subscription, run the following:

```bash
az account set --subscription turingmybinder
```

## Create a Resource Group

Azure groups related resources together by assigning them a Resource Group.
We need to create one for Hub23.

```bash
az group create --name Hub23 --location westeurope --output table
```

- `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
- `--location` sets the [region of data centres](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
- `--output table` prints the info in a human-readable format.

```{note}
If you have already followed the docs on creating a key vault, then this resource group should already exist and this step can be skipped.
```
