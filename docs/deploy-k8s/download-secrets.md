(content:k8s:download-secrets)=
# Download the required secrets

We will require some info from the key vault in order to deploy the Kubernetes cluster and the BinderHub.

## Create a secrets folder

Create a folder in which to download the secrets so.
This will be git-ignored.

```bash
mkdir .secret
```

## Download the secrets

We will require the following secrets:

- Service Principal app ID and key
- public SSH key

They should be downloaded to files in the `.secret` folder so that they are git-ignored.

Download the Service Principal:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name appId \
    --file .secret/appId.txt
```

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name appKey \
    --file .secret/appKey.txt
```

Download the public SSH key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```
