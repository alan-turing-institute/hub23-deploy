(content:connect-container-registry)=
# Connect a Container Registry

This section explains how to connect a container registry (either Docker Hub or Azure Container Registry) to BinderHub.

```{note}
Don't forget to delete the local copies of the secrets once you're finished with them.
```

## Docker Hub

To attach a Docker Hub account to the BinderHub, add the following to `.secret/secret.yaml` (under `config` key if using `deploy/prod-template.yaml`), where `{docker-id}` is your ID (**not** the associated e-mail address).
This account **must** be a member of the `binderhubtest` DockerHub organisation.

```yaml
registry:
  username: {docker-id}
  password: {password}
```

If adding to `deploy/prod-template.yaml`, use `sed` to input these variables.

## Azure Container Registry (ACR)

To use an ACR, we provide the BinderHub with the Service Principal so that it can login with the correct permissions.

Update `deploy/config.yaml` (under the `config` key if using `deploy/prod.yaml`) with the following:

```yaml
BinderHub:
  use_registry: true
  image_prefix: hub23-registry.azurecr.io/hub23/binder-dev-
DockerRegistry:
  token_url: "https://hub23-registry.azurecr.io/oauth2/token?service=hub23-registry.azurecr.io"
registry:
    url: https://hub23-registry.azurecr.io
```

In `deploy/secret-template.yaml` (under `config` key if using `deploy/prod-template.yaml`), `{username}` and `{password}` will be replaced with the Service Principal app ID and key, respectively.

```yaml
registry:
  username: {docker-id}
  password: {password}
```
