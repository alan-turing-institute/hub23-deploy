(content:binderhub:github-api-limit)=
# Increasing GitHub API limit

```{note}
This step is not strictly necessary though is recommended before sharing the Binder link with others.
```

By default, GitHub allows 60 API requests per hour.
We can create an Access Token to authenticate the BinderHub and hence increase this limit to 5,000 requests an hour.
This is advisable if you are expecting users to hosts repositories on your BinderHub.

## Create a Personal Access Token

Create a new token with default,read-pnly permissions (do not check any boxes) [here](https://github.com/settings/tokens/new/).

Immediately copy the token as you will not be able to see it again!

## Add the token to the Azure Keyvault

Save the token to the Azure key vault.

```bash
az keyvault secret set \
  --vault-name hub23-keyvault \
  --name binderhub-access-token \
  --value <PASTE-TOKEN-HERE>
```

Download the secret like so:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name binderhub-access-token \
    --file .secret/accessToken.txt
```

## Update `secret-template.yaml` or `deploy/prod-template.yaml`

Update your template file with the following.

```yaml
jupyterhub:
  config:
    GitHubRepoProvider:
      access_token: {accessToken}
```

Again, we can use `sed` to populate this secret:

```bash
sed -e "s/{accessToken}/$(cat .secret/accessToken.txt)/" \
    deploy/secret-template.yaml > .secret/secret.yaml
```

### Delete the local copy

Remember to delete the local copy after populating `.secret/secret.yaml`.

```bash
rm .secret/accessToken.txt
```
