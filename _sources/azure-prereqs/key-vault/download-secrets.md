(content:key-vault:download-secrets)=
# Downloading Secrets from the Key Vault

## Saving secrets to files

We can download the secrets and save them to files like so.
They should be downloaded into the `.secret/` folder so that they are git-ignored.
We will need certain secrets in order to create the `config.yaml` and `secret.yaml` files to deploy and upgrade Hub23.

## Download the SSH keys

Download the private key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-hub23cluster-private \
    --file .secret/ssh-key-hub23cluster
```

Download the public key:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name ssh-key-hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```

### Download the API and secret tokens

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

## Saving secrets to bash variables

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

```{note}
Here, `tsv` stands for 'Tab Separated Variable'.
```
