# hub23-deploy

A repo to manage the private Turing BinderHub instance, Hub23.

[![Build Status](https://dev.azure.com/hub23/hub23-deploy/_apis/build/status/alan-turing-institute.hub23-deploy?branchName=master)](https://dev.azure.com/hub23/hub23-deploy/_build/latest?definitionId=1&branchName=master)

- [Hub23 Helm Chart](#hub23-helm-chart)
- [Developing Hub23](#developing-hub23)
  - [Requirements](#requirements)
  - [Changing `hub23-chart`](#changing-hub23-chart)
- [Scripts](#scripts)
  - [Pre-Commit Hook](#pre-commit-hook)
- [Things of Use](#things-of-use)
  - [Useful commands](#Useful-commands)
  - [Restarting the JupyterHub](#Restarting-the-JupyterHub)

---

## Hub23 Helm Chart

This repo contains the local Helm Chart that configures the Hub23 BinderHub deployment: [`hub23-chart`](hub23-chart).

The [HelmUpgradeBot](https://github.com/HelmUpgradeBot/hub23-deploy-upgrades) automatically opens Pull Requests to this repository that update the dependencies of the Helm Chart in [`hub23-chart/requirements.yaml`](hub23-chart/requirements.yaml).

Upon merging the PR, the [Azure Pipelines configuration](azure-pipelines.yml) automatically applies the updated Helm Chart to the Kubernetes cluster running Hub23.

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
- `azure-pipelines.yml` and `scripts/generate_configs.py` are updated in order to populate the template with the appropriate information.

This will ensure that the Hub23 deployment is kept up-to-date with the repo, and a future developer (someone else or future-you!) can recreate the configuration files for Hub23.

## Scripts

The `scripts` folder contains some Python files that make interacting with Hub23 slightly easier.

These scripts require Python version 3.7 and the `pyyaml` package which can be installed by running:

```bash
pip install -r requirements.txt
```

`generate-configs.py` is a Python script to automatically recreate the configuration files in order to maintain or upgrade Hub23.

```bash
python generate-configs.py \
    --vault-name [-v] VAULT-NAME \
    --registry-name [-r] REGISTRY-NAME \
    --image-prefix [-p] IMAGE-PREFIX \
    --jupyterhub-ip [-j] JUPYTERHUB-IP-ADDRESS \
    --binder-ip [-b] BINDER-IP-ADDRESS \
    --identity
```

where:

- `VAULT-NAME` is the Azure Key Vault where secrets are kept;
- `REGISTRY-NAME` is the Azure Container Registry to connect to the BinderHub;
- `IMAGE-PREFIX` is an identifier to prepend to Docker images;
- `JUPYTERHUB-IP-ADDRESS` is the JupyterHub IP address, or A record;
- `BINDER-IP` is the Binder page IP address, or A record; and
- `--identity` is a flag to tell the script to login to Azure using a Managed System Identity.

`generate-configs.py` will populate `deploy/prod-template.yaml` with the appropriate information and save the output as `.secret/prod.yaml`.

`.secret/` is a git-ignored folder so that the secrets contained in `.secret/prod.yaml` cannot be pushed to GitHub.

`upgrade.py` is a script to apply the updated Helm Chart to Hub23's Kubernetes cluster.

```bash
python upgrade.py \
    --hub-name [-n] HUB-NAME \
    --chart-name [-z] CHART-NAME \
    --cluster-name [-c] CLUSTER-NAME \
    --resource-group [-g] RESOURCE-GROUP \
    --subscription [-s] SUBSCRIPTION \
    --identity \
    --dry-run \
    --debug
```

where:

- `HUB-NAME` is the name of the deployed BinderHub (i.e. `hub23`);
- `CHART-NAME` is the name of the local Helm Chart;
- `CLUSTER-NAME` is the name of the Azure Kubernetes cluster Hub23 is running on;
- `RESOURCE-GROUP` is the Azure Resource Group;
- `SUBSCRIPTION` is the Azure subscription name;
- `--identity` is a flag to tell the script to login to Azure using a Managed System Identity;
- ``--dry-run` will perform a dry-run of the upgrade; and
- `--debug` will provide debugging output from the `helm upgrade` command.

### Pre-Commit Hook

If modifying the Python scripts, you can install a git pre-commit hook to ensure the files conform to PEP8 standards.

To install the pre-commit hook, do the following.

```bash
pip install -r requirements-dev.txt
pre-commit install
```

[Black](https://github.com/psf/black) and [Flake8](http://flake8.pycqa.org/en/latest/) will then be applied to every commit effecting Python files.

## Things of Use

### Useful commands

To access the JupyterHub logs:

```bash
python logs.py \
    --hub-name [-n] HUB-NAME \
    --cluster-name [-c] CLUSTER-NAME \
    --resource-group [-g] RESOURCE-GROUP \
    --identity
```

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
