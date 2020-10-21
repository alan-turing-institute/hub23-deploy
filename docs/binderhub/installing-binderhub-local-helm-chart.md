# Installing BinderHub with a Local Helm Chart

This documentation walks through the steps required to install a BinderHub using a local helm chart.

In ["Installing BinderHub"]({{ site.baseurl }}{% post_url 2010-01-06-installing-binderhub %}), BinderHub was installed and configured by using the [BinderHub chart](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub) directly.
By writing a helm chart that _depends_ on the BinderHub chart, we can later introduce other helm charts to increase the functionality of Hub23.

This documentation assumes you have the following CLI's installed:

- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm)

## Table of Contents

- [Downloading the Required Secrets](#downloading-the-required-secrets)
- [Writing the `hub23-chart` Helm Chart](#writing-the-hub23-chart-helm-chart)
- [Configuring Hub23](#configuring-hub23)
- [Installing `hub23-chart`](#installing-hub23-chart)
- [Upgrading `hub23-chart`](#upgrading-hub23-chart)
- [Increasing GitHub API limit](#increasing-github-api-limit)
- [Customisations](#customisations)

---

## Downloading the Required Secrets

To set up the BinderHub, we will need to download the API and secret tokens from the keyvault like so:

```bash
az keyvault secret download --vault-name hub23-keyvault --name apiToken --file .secret/apiToken.txt
```

```bash
az keyvault secret download --vault-name hub23-keyvault --name secretToken --file .secret/secretToken.txt
```

## Writing the `hub23-chart` Helm Chart

#### 1. Create a directory to store the chart in

```bash
mkdir hub23-chart
```

#### 2. Create `hub23-chart/Chart.yaml`

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

#### 3. Create `hub23-chart/requirements.yaml`

`requirements.yaml` is where we define which other charts we are dependent on, e.g. BinderHub.

```yaml
dependencies:
- name: binderhub
  repository: https://jupyterhub.github.io/helm-chart
  version: 0.2.0-1efa7b8
```

**NOTE:** The `version` field should be up-to-date from [this list](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).
{: .notice--info}

#### 4. Create `hub23-chart/values.yaml`

`values.yaml` is where we define the default values of our chart.

```yaml
rbac:
  enabled: true

binderhub:
  config:
    BinderHub:
      use_registry: true
```

**NOTE:** Now we are no longer using the BinderHub chart directly, we reference changes we want to make to the BinderHub chart with the top level key `binderhub`.
{: .notice--info}

#### 5. Add `hub23-chart/.helmignore`

Updating and installing the helm chart will generate a lot of artefacts that we don't want pushing to GitHub.
Add the [`.helmignore` file](https://github.com/helm/helm/blob/master/pkg/repo/repotest/testdata/examplechart/.helmignore) to prevent this.

## Configuring Hub23

#### 1. Create `deploy/prod.yaml`

This file is the same as `deploy/config.yaml` in ["Installing BinderHub"]({{ site.baseurl }}{% post_url 2010-01-06-installing-binderhub %}), but we are now calling it `prod` to indicate production status.

```yaml
projectName: hub23

binderhub:
  config:
    BinderHub:
      image_prefix: hub23registry.azurecr.io/hub23/binder-dev-
      hub_url: http://HUB_URL

    DockerRegistry:
      token_url: "https://hub23registry.azurecr.io/oauth2/token?service=hub23registry.azurecr.io"

  registry:
    url: https://hub23registry.azurecr.io
```

#### 2. Create `deploy/prod-template.yaml`

This file performs the same role as `deploy/secret-template.yaml` in ["Installing BinderHub"]({{ site.baseurl }}{% post_url 2010-01-06-installing-binderhub %}).

```yaml
binderhub:
  registry:
    username: {username}
    password: {password}

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

#### 1. Update the chart's dependencies

```bash
cd hub23-chart && helm dependency update && cd ..
```

#### 2. Install the helm chart

```bash
helm install ./hub23-chart \
    --name hub23 \
    --namespace hub23 \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml
```

## Upgrading `hub23-chart`

#### 1. Update the chart's dependencies

```bash
cd hub23-chart && helm dependency update && cd ..
```

#### 2. Upgrade the helm chart itself

```bash
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml
```

## Increasing GitHub API limit

**NOTE:** This step is not strictly necessary though is recommended before sharing the Binder link with others.
{: .notice--info}

By default, GitHub allows 60 API requests per hour.
We can create an Access Token to authenticate the BinderHub and hence increase this limit to 5,000 requests an hour.
This is advisable if you are expecting users to hosts repositories on your BinderHub.

#### 1. Create a Personal Access Token

Create a new token with default,read-pnly permissions (do not check any boxes) [here](https://github.com/settings/tokens/new/).

Immediately copy the token as you will not be able to see it again!

#### 2. Add the token to the Azure Keyvault

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

#### 3. Update `secret-template.yaml`

Update `deploy/prod-template.yaml` with the following.

```yaml
jupyterhub:
  config:
    GitHubRepoProvider:
      access_token: {accessToken}
```

Again, we can use `sed` to populate this secret:

```bash
sed -e "s/{accessToken}/$(cat .secret/accessToken.txt)/" \
    deploy/prod-template.yaml > .secret/prod.yaml
```

#### Delete the local copy

Remember to delete the local copy after populating `.secret/prod.yaml`.

```bash
rm .secret/accessToken.txt
```

#### 4. Upgrade the `helm` chart

Follow the steps in [Upgrading `hub23-chart`](#upgrading-hub23-chart) to upgrade.

## Customisations

Any customisations described in the following documents can be applied to this setup.
Just be vigilant with your indentation!

- ["Customising the JupyterHub"]({{ site.baseurl }}{% post_url 2010-01-09-customise-jupyterhub %})
- ["Enabling Authentication"]({{ site.baseurl }}{% post_url 2010-01-10-enabling-authentication %})
- ["Changing the logo on the Binder Page"]({{ site.baseurl }}{% post_url 2010-01-11-changing-logo %})
- ["Enabling Page Redirection"]({{ site.baseurl }}{% post_url 2010-01-12-enabling-page-redirection %})
- ["Optimizing the JupyterHub for Autoscaling"]({{ site.baseurl }}{% post_url 2010-01-13-optimising-autoscaling %})