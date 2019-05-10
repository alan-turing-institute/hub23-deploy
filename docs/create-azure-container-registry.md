# Creating an Azure Container Registry and connecting to the Kubernetes Cluster

:construction: :construction: This documentation is a work in progress :construction: :construction:

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

**N.B.:** Can be skipped if the Resource Group already exists.

#### 4. Create an ACR

ACR name must be globally unique and consist of only lowercase alphanumeric characters, between 5 and 50 characters long.

```
az acr create --name hub23registry --resource-group Hub23 --sku Standard
```

Note the following value: `loginServer: hub23-registry.azurecr.io`.

#### 5. Login to the ACR

```
az acr login --name hub23registry
```

#### 6. Get ACR resource ID

Keep a note of this output for the next step.

```
az acr show --resource-group Hub23 --name hub23registry --query "id" --output tsv
```

#### 7. Create a Kubernetes secret to access the ACR

```
kubectl create secret docker-registry hub23-docker-decret \
    --docker-server hub23registry.azurecr.io \
    --docker-email hub23registry@turing.ac.uk \
    --docker-username=$(cat .secret/appID.txt) \
    --docker-password $(cat .secret/key.txt)
```

az acr update -n hub23registry --admin-enabled true

az acr credential show -n hub23registry

Update `secret.yaml`

The value of `password` is copied from `az acr credential show` command.

```
jupyterhub:
  hub:
    services:
      binder:
        apiToken: "xxxxxx"
  proxy:
    secretToken: "xxxxxx"
registry:
  url: https://binderhubregistry.azurecr.io
  password: |
    {
      "passwords": [
        {
          "name": "password",
          "value": "xxxxxx"
        },
        {
          "name": "password2",
          "value": "xxxxxx"
        }
      ],
      "username": "binderHubRegistry"
    }
```
