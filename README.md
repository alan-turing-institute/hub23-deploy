# hub23-deploy

A repository to manage the private Turing BinderHub instance, Hub23.

| | :recycle: CI Status |
| --- | --- |
| :money_with_wings: Subscription | [![Build Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/Azure%20Subscription%20Status?branchName=main)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=5&branchName=main) |
| :rocket: Deployment | [![Deploy Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/Deploy%20upgrade%20to%20Hub23?branchName=main)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=1&branchName=main) |
| :broom: Linting and Formatting | [![Lint and Format](https://github.com/alan-turing-institute/hub23-deploy/actions/workflows/lint-format.yml/badge.svg)](https://github.com/alan-turing-institute/hub23-deploy/actions/workflows/lint-format.yml) |
| :notebook: Docs | [![Build and Publish JupyterBook Docs](https://github.com/alan-turing-institute/hub23-deploy/workflows/Build%20and%20Publish%20JupyterBook%20Docs/badge.svg)](https://github.com/alan-turing-institute/hub23-deploy/actions?query=workflow%3A%22Build+and+Publish+JupyterBook+Docs%22+branch%3Amain) |

**Table of Contents:**

- [:wheel_of_dharma: Hub23 Helm Chart](#wheel_of_dharma-hub23-helm-chart)
- [:rocket: Developing Hub23](#rocket-developing-hub23)
  - [:pushpin: Requirements](#pushpin-requirements)
  - [:repeat: Changing `hub23-chart`](#repeat-changing-hub23-chart)
- [:question: How-To's](#question-how-tos)
  - [:house_with_garden: Work Locally](#house_with_garden-work-locally)
  - [:electric_plug: Connect to Kubernetes](#electric_plug-connect-to-kubernetes)
- [:computer: Code Snippets](#computer-code-snippets)
  - [:dizzy: Restarting the JupyterHub](#dizzy-restarting-the-jupyterhub)
  - [:leftwards_arrow_with_hook: Pre-Commit Hook](#leftwards_arrow_with_hook-pre-commit-hook)
  - [:money_with_wings: Billing](#money_with_wings-billing)
- [:books: Documentation](#books-documentation)

---

## :wheel_of_dharma: Hub23 Helm Chart

This repository contains the local Helm Chart that configures the Hub23 BinderHub deployment: [`hub23-chart`](hub23-chart).

The [HelmUpgradeBot](https://github.com/HelmUpgradeBot/hub23-deploy-upgrades) automatically opens Pull Requests to this repository that update the dependencies of the Helm Chart in the [`requirements.yaml`](hub23-chart/requirements.yaml) file.

Upon merging the Pull Request, the [Continuous Deployment Azure Pipeline](.az-pipelines/cd-pipeline.yml) automatically applies the updated Helm Chart to the Kubernetes cluster running Hub23.

## :rocket: Developing Hub23

Please read the :purple_heart:[Code of Conduct](CODE_OF_CONDUCT.md):purple_heart: and :space_invader:[Contributing Guidelines](CONTRIBUTING.md):space_invader: before you begin developing.

### :pushpin: Requirements

Three command line interfaces are used to manage Hub23:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) - to manage the Azure compute resources
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl) - to manage the Kubernetes cluster
- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm) - to manage the BinderHub application running on the Kubernetes cluster

### :repeat: Changing `hub23-chart`

If changes are made during development, make sure that:

- the new format is reflected in [`deploy/prod-template.yaml`](deploy/prod-template.yaml) and any new secrets/tokens/passwords are redacted;
- new secrets/tokens/passwords are added to the Azure Key Vault (see the [Key Vault docs](https://alan-turing-institute.github.io/hub23-deploy/azure-keyvault/)); and
- [`.az-pipelines/cd-pipeline.yml`](.az-pipelines/cd-pipeline.yml) and [`cli-tool/hub_manager/hub_manager.py`](cli-tool/hub_manager/hub_manager.py) are updated in order to populate the template with the appropriate information.

This will ensure that the Hub23 deployment is kept up-to-date with the repo, and a future developer (someone else or future-you!) can recreate the configuration files for Hub23.

## :question: How-To's

### :house_with_garden: Work Locally

**If you DO have write access:** :black_nib:

```bash
# Clone this repository
git clone https://github.com/alan-turing-institute/hub23-deploy.git
cd hub23-deploy

# Create a new branch
git checkout -b NEW_BRANCH_NAME
```

And you're ready to go! :tada:

**If you DON'T have write access:** :no_good:

1. Click "Fork" in the top-right corner of the browser window
2. Select your GitHub username as the fork destination
3. Clone the forked repository

```bash
# Clone your fork
git clone https://github.com/YOUR_GITHUB_USERNAME/hub23-deploy.git
cd hub23-deploy

# Create a new branch
git checkout -b NEW_BRANCH_NAME
```

### :electric_plug: Connect to Kubernetes

This section uses the [Azure CLI](#pushpin-requirements).

1. Login to Azure

    ```bash
    az login
    ```

2. Set the Azure subscription

    ```bash
    az account set --subscription Turing-BinderHub
    ```

3. Connect to the cluster

    ```bash
    az aks get-credentials --name hub23cluster --resource-group Hub23
    ```

## :computer: Code Snippets

To find out more info about a Kubernetes pod:

```bash
kubectl --namespace hub23 describe pod POD_NAME
```

### :dizzy: Restarting the JupyterHub

If the Hub is being problematic, for example, throwing "Internal Server Error" messages or not spinning up user nodes, it can be restarted with the following commands.

Scale down the Hub:

```bash
kubectl --namespace hub23 scale deployment hub --replicas=0
```

Wait until the `hub-` pod has been terminated.
Use `kubectl --namespace hub23 get pods` to check its status.

Scale the Hub back up:

```bash
kubectl --namespace hub23scale deployment hub --replicas=1
```

### :leftwards_arrow_with_hook: Pre-Commit Hook

If modifying the Python scripts, you can install a git pre-commit hook to ensure the files conform to PEP8 standards.

To install the pre-commit hook, do the following:

```bash
# Install the development requirements
pip install -r dev-requirements.txt

# Install the pre-commit configuration
pre-commit install
```

[Black](https://github.com/psf/black) and [Flake8](http://flake8.pycqa.org/en/latest/) will then be applied to every commit effecting Python files.

### :money_with_wings: Billing

The [`billing`](./billing) subdir contains resources for calculating running costs of Hub23.

## :books: Documentation

The Deployment Guide docs for Hub23 are stored in the [`docs`](./docs) folder.
A [GitHub Action workflow](.github/workflows/build-docs.yml) renders the documentation using [Jupyter Book](https://jupyterbook.org) and publishes it to the `gh-pages` branch of the repo to be hosted at https://alan-turing-institute.github.io/hub23-deploy
