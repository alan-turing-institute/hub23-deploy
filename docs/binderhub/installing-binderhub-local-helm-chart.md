(content:binderhub:local-chart)=
# Installing BinderHub with a Local Helm Chart

This documentation walks through the steps required to install a BinderHub using a local helm chart.
By writing a helm chart that _depends_ on the BinderHub chart, we can later introduce other helm charts to increase the functionality of Hub23.

## Downloading the Required Secrets

To set up the BinderHub, we will need to download the API and secret tokens from the keyvault like so:

```bash
az keyvault secret download --vault-name hub23-keyvault --name apiToken --file .secret/apiToken.txt
```

```bash
az keyvault secret download --vault-name hub23-keyvault --name secretToken --file .secret/secretToken.txt
```

## Writing the `hub23-chart` Helm Chart

### Create a directory to store the chart in

```bash
mkdir hub23-chart
```

### Create `hub23-chart/Chart.yaml`

```yaml
apiVersion: v1
name: hub23-chart
version: 0.0.1
description: A meta-chart for the BinderHub deployment on Hub23
sources:
  - https://github.com/alan-turing-institute/hub23-deploy
maintainers:
  - name: your-name
    email: your-email@whatever.com
```

### Create `hub23-chart/requirements.yaml`

`requirements.yaml` is where we define which other charts we are dependent on, e.g. BinderHub.

```yaml
dependencies:
- name: binderhub
  repository: https://jupyterhub.github.io/helm-chart
  version: 0.2.0-1efa7b8
```

```{note}
The `version` field should be up-to-date from [this list](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).
```

### Create `hub23-chart/values.yaml`

`values.yaml` is where we define the default values of our chart.

```yaml
rbac:
  enabled: true

binderhub:
  config:
    BinderHub:
      use_registry: true
```

```{note}
Now we are no longer using the BinderHub chart directly, we reference changes we want to make to the BinderHub chart with the top level key `binderhub`.
```

### Add `hub23-chart/.helmignore`

Updating and installing the helm chart will generate a lot of artefacts that we don't want pushing to GitHub.
Add the [`.helmignore` file](https://github.com/helm/helm/blob/master/pkg/repo/repotest/testdata/examplechart/.helmignore) to prevent this.

## Configuring Hub23

### Create `deploy/prod.yaml`

`deploy/prod.yaml` is where we will overwrite the chart with our non-secret values.

```yaml
projectName: hub23

binderhub:
  config:
    BinderHub:
      image_prefix: "IMAGE_PREFIX"
      hub_url: "http://HUB_URL"
```

```{note}
See {ref}`content:binderhub:connect-container-registry` for how to connect your registry in this file.
```

### Create `deploy/prod-template.yaml`

`deploy/prod-template.yaml` will include our secret values.

```yaml
binderhub:
  registry:
    username: "{username}"
    password: "{password}"

  jupyterhub:
    hub:
      services:
        binder:
          apiToken: "{apiToken}"
    proxy:
      secretToken: "{secretToken}"
```

`sed` commands or the [`hub-manager` CLI](https://github.com/alan-turing-institute/hub23-deploy/blob/master/cli-tool/hub_manager/README.md) can be used to populate this template and save it to `.secret/`.

## Installing `hub23-chart`

### Update the chart's dependencies

```bash
cd hub23-chart && helm dependency update && cd ..
```

### Install the helm chart

```bash
helm install ./hub23-chart \
    --name hub23 \
    --namespace hub23 \
    --create-namespace \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml \
    --cleanup-on-fail
```

## Upgrading `hub23-chart`

### Update the chart's dependencies

```bash
cd hub23-chart && helm dependency update && cd ..
```

### Upgrade the helm chart itself

```bash
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml \
    --cleanup-on-fail
```
