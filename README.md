# hub23-deploy

A repo to manage the private Turing BinderHub instance, Hub23.

| | Status |
| --- | --- |
| Subscription | [![Build Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/Azure%20Subscription%20Status?branchName=master)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=5&branchName=master) |
| Deployment | [![Deploy Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/Deploy%20upgrade%20to%20Hub23?branchName=master)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=1&branchName=master) |
| Helm Chart | [![Lint Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/Lint%20and%20Validate%20Helm%20Chart?branchName=master)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=4&branchName=master) |
| Python Scripts | ![GitHub Actions - Black](https://github.com/alan-turing-institute/hub23-deploy/workflows/Black/badge.svg) ![GitHub Actions - Flake8](https://github.com/alan-turing-institute/hub23-deploy/workflows/Flake8/badge.svg) |

- [Hub23 Helm Chart](#hub23-helm-chart)
- [Developing Hub23](#developing-hub23)
  - [Requirements](#requirements)
  - [Changing `hub23-chart`](#changing-hub23-chart)
- [Things of Use](#things-of-use)
  - [Restarting the JupyterHub](#Restarting-the-JupyterHub)
  - [Pre-Commit Hook](#pre-commit-hook)
  - [Billing](#billing)

---

## Hub23 Helm Chart

This repo contains the local Helm Chart that configures the Hub23 BinderHub deployment: [`hub23-chart`](hub23-chart).

The [HelmUpgradeBot](https://github.com/HelmUpgradeBot/hub23-deploy-upgrades) automatically opens Pull Requests to this repository that update the dependencies of the Helm Chart in [`hub23-chart/requirements.yaml`](hub23-chart/requirements.yaml).

Upon merging the PR, the [Azure Pipelines configuration](.az-pipelines/cd-pipeline.yml) automatically applies the updated Helm Chart to the Kubernetes cluster running Hub23.

## Developing Hub23

### Requirements

Three command line interfaces are used to manage Hub23:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) - to manage the Azure compute resources
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl) - to manage the Kubernetes cluster
- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm) - to manage the BinderHub application running on the Kubernetes cluster

### Changing `hub23-chart`

If changes are made to `.secret/prod.yaml` during development, make sure that:

- the new format is reflected in `deploy/prod-template.yaml` and any new secrets/tokens/passwords are redacted;
- new secrets/tokens/passwords are added to the Azure Key Vault (see `docs/azure-keyvault.md`); and
- [`.az-pipelines/cd-pipeline.yml`](.az-pipelines/cd-pipeline.yml) and [`cli-tool/hub_manager/hub_manager.py`](cli-tool/hub_manager/hub_manager.py) are updated in order to populate the template with the appropriate information.

This will ensure that the Hub23 deployment is kept up-to-date with the repo, and a future developer (someone else or future-you!) can recreate the configuration files for Hub23.

## Things of Use

To find out more info about a Pod:

```bash
kubectl describe pod <POD-NAME> --namespace hub23
```

### Restarting the JupyterHub

If the Hub is being problematic, for example, throwing "Internal Server Error" messages or not spinning up user nodes, it can be restarted with the following commands.

Scale down the Hub:

```bash
kubectl scale deployment hub --replicas=0 --namespace hub23
```

Wait until the `hub-` pod has been terminated.
Use `kubectl get pods --namespace hub23` to check it's status.

Scale the Hub back up:

```bash
kubectl scale deployment hub --replicas=1 --namespace hub23
```

### Pre-Commit Hook

If modifying the Python scripts, you can install a git pre-commit hook to ensure the files conform to PEP8 standards.

To install the pre-commit hook, do the following.

```bash
pip install -r dev-requirements.txt
pre-commit install
```

[Black](https://github.com/psf/black) and [Flake8](http://flake8.pycqa.org/en/latest/) will then be applied to every commit effecting Python files.

### Billing

The `billing` subdir contains resources for calculating running costs of Hub23.
