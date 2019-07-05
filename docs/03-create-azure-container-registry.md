# Creating an Azure Container Registry and connecting to the Kubernetes Cluster

This document walks through the creation of an Azure Container Registry for the Turing BinderHub (Hub23) and how to connect it to the BinderHub/Kubernetes cluster.

It assumes you have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) installed.

#### 1. Login to Azure

```
az login --output none
```

Login with your Turing account.

#### 2. Set subscription

To see a list of your subscriptions, run the following command.

```
az account list --refresh --output table
```

Activate the BinderHub subscription with the following command.

```
az account set -s Turing-BinderHub
```

#### 3. Create Resource Group

```
az group create --name Hub23 --location westeurope
```

**NOTE:** This step can be skipped if the Resource Group already exists.

#### 4. Create an ACR

The ACR name must be globally unique and consist of only lowercase alphanumeric characters, between 5 and 50 characters long.
This can be checked using: `az acr check-name --name <ACR-NAME>`.

```
az acr create --name hub23registry --resource-group Hub23 --sku Standard
```

#### 5. Login to the ACR

```
az acr login --name hub23registry
```

#### 6. Save the login server to a variable

```
LOGIN_SERVER=$(az acr show --name hub23-registry --query loginServer --output tsv)
```

#### 7. Save the registry ID to a variable

```
ACR_ID=$(az acr show --name hub23-registry --query is --output tsv)
```

#### 8. Assign AcrPush role to the Service Principal

The Service Principal needs an AcrPush role so that it is permitted to both push and pull images to/from the registry.
Without this, BinderHub won't be able to store the images it generates.

**NOTE:** You will only have permission to perform this step if you are an owner on the Turing-BinderHub Azure subscription.
Otherwise, you should add IT to assign this role to the Service Principal.

```
# First download the Service Principal Client ID
az key-vault secret download --vault-name hub23-keyvault --name SP-appID --file .secret/sp-appID.txt

# Then create the AcrPush role
az role assignment create --assignee $(cat .secret/sp-appID.txt) --scope $ACR_ID --role AcrPush
```

#### 9. Update `secret.yaml`

Now we provide the BinderHub with the Service Principal so that it can login to the ACR.

```
az key-vault secret download --vault-name hub23-keyvault --name SP-key --file .secret/sp-key.txt
```

Update `.secret/secret.yaml` with the following:

```
registry:
    url: https://hub23-registry.azurecr.io
    username: $(cat .secret/sp-appID.txt)
    password: $(cat .secret/key.txt)
```

**NOTE:** Don't forget to delete the local copies of the Service Principal once you're finished with them.

#### 10. Update `config.yaml`

Add the following to `.secret/config.yaml`:

```
config:
  BinderHub:
    use_registry: true
    image_prefix: hub23-registry.azurecr.io/hub23/binder-dev-
  DockerRegistry:
    token_url: "https://hub23-registry.azurecr.io/oauth2/token?service=hub23-registry.azurecr.io"
```

#### 11. Upgrade the BinderHub deployment

```
helm upgrade hub23 jupyterhub/binderhub --version=<commit-hash> -f .secret/secret.yaml -f .secret/config.yaml
```

Test out the ACR by building a Binder instance.
