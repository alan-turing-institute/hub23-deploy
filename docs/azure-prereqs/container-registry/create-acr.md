(content:container-registry:create)=
# Create an Azure Container Registry

## Login to Azure

```bash
az login --username YOUR_TURING_EMAIL --output none
```

Login with your Turing account.

## Set subscription

To see a list of your subscriptions, run the following command.

```bash
az account list --refresh --output table
```

Activate the BinderHub subscription with the following command.

```bash
az account set --subscription turingmybinder
```

## Create Resource Group

```bash
az group create --name Hub23 --location westeurope
```

```{note}
This step can be skipped if the Resource Group already exists.
```

## Create an ACR

The ACR name must be globally unique and consist of only lowercase alphanumeric characters, between 5 and 50 characters long.
This can be checked using: `az acr check-name --name <ACR-NAME>`.

```bash
az acr create --name hub23registry --resource-group Hub23 --sku Standard
```

## Login to the ACR

```bash
az acr login --name hub23registry
```

## Save the login server to a variable

```bash
LOGIN_SERVER=$(az acr show --name hub23-registry --query loginServer --output tsv)
```

## Save the registry ID to a variable

```bash
ACR_ID=$(az acr show --name hub23-registry --query id --output tsv)
```

## Assign AcrPush role to the Service Principal

The Service Principal needs an AcrPush role so that it is permitted to both push and pull images to/from the registry.
Without this, BinderHub won't be able to store the images it generates.

```{warning}
You will only have permission to perform this step if you are an owner on the turingmybinder Azure subscription.
Otherwise, you should ask IT to assign this role to the Service Principal.
```

```bash
# First download the Service Principal Client ID
az key-vault secret download --vault-name hub23-keyvault --name SP-appID --file .secret/sp-appID.txt

# Then create the AcrPush role
az role assignment create --assignee $(cat .secret/sp-appID.txt) --scope $ACR_ID --role AcrPush
```
