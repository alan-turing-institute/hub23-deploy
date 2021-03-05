(content:container-registry:create)=
# Create an Azure Container Registry

## Create an ACR

```{note}
The ACR name must be globally unique and consist of only lowercase alphanumeric characters, between 5 and 50 characters long.
This can be checked using: `az acr check-name --name <ACR-NAME>`.
```

```bash
az acr create --name hub23registry --resource-group hub23 --sku Standard
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
You will only have permission to perform this step if you are an owner on the `turingmybinder` Azure subscription.
Otherwise, you should ask IT to assign this role to the Service Principal.
```

See the {ref}`content:key-vault:service-principals` section for instructions on how to download the Service Principal app ID to a file from the Key Vault.

```bash
az role assignment create --assignee $(cat .secret/appId.txt) --scope ${ACR_ID} --role AcrPush
```
