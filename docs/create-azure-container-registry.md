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

Note the following values: `loginServer`.

#### 5. Get ACR resource ID

Keep a note of this output for the next step.

```
az acr show --resource-group Hub23 --name hub23registry --query "id" --output tsv
```

#### 6. Grant access for the Kubernetes cluster to pull images stored in ACR

```
az role assignment create --assignee $(cat .secret/SP-appID.txt) --scope <acrID> --role acrpull
```

where `<acrID>` is the output of Step 5.

**This step does not work.**
**Need a different Service Principal to create role assignments for the ACR.**

**Make sure you're logged into the ACR!!**