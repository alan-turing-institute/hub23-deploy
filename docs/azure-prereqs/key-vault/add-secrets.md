(content:key-vault:add-secrets)=
# Adding secrets to the Key Vault

Hub23 requires some secrets, passwords, tokens etc. for functionality.

- SSH keys for accessing the Kubernetes cluster
- API and secret token

## Create a secrets folder

Create a folder to save secret files to. This will be git-ignored by this repo.

```bash
mkdir .secret/
```

## Generate the SSH keys

The following command will generate a pair of ssh keys, one private and one public (appended with `.pub`), and save them to files in the `.secret/` folder.

```bash
ssh-keygen --file .secret/ssh-key-hub23cluster
```

We have appended the file names with `hub23cluster` which is the cluster name we will assign to the Kubernetes cluster on deployment.
The name follows the same rule as the key vault.

## Add the SSH keys to the vault

Add the private key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name ssh-key-hub23cluster-private \
    --file .secret/ssh-key-hub23cluster
```

Add the public key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name ssh-key-hub23cluster-public \
    --file .secret/ssh-key-hub23cluster.pub
```

**Now delete the local copies of the SSH keys.**

```bash
rm .secret/ssh-key-hub23cluster*
```

## Add API and secret tokens to the vault

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
