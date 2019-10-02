# hub23-deploy

A repo to manage the private Turing BinderHub instance, Hub23.

- [Requirements](#Requirements)
- [Usage](#Usage)
- [Maintaining or Upgrading Hub23](#Maintaining-or-Upgrading-Hub23)
- [Restarting the JupyterHub](#Restarting-the-JupyterHub)
- [Useful commands](#Useful-commands)
- [Changelog](#Changelog)

---

## Requirements

Three command line interfaces are used to manage Hub23:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) - to manage the Azure compute resources
- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl) - to manage the Kubernetes cluster
- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm) - to manage the BinderHub application running on the Kubernetes cluster

The scripts in this repo require Python version 3.7 and the `pyyaml` package which can be installed by running:

```bash
pip install -r requirements.txt
```

## Usage

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

## Maintaining or Upgrading Hub23

If changes are made to `.secret/prod.yaml` during development, make sure that:

- the new format is reflected in `deploy/prod-template.yaml` and any new secrets/tokens/passwords are redacted;
- new secrets/tokens/passwords are added to the Azure Key Vault (see `docs/azure-keyvault.md`); and
- `generate-configs.py` is updated in order to populate the template with the appropriate information.

This will ensure that a future developer (someone else or future-you!) can recreate the configuration files for Hub23.

To upgrade the BinderHub Helm Chart:

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

`upgrade.py` upgrades the deployment helm chart.

## Restarting the JupyterHub

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

## Useful commands

To print the pods and IP addresses of the Binder page and JupyterHub:

```bash
python info.py \
    --hub-name [-n] HUB-NAME \
    --cluster-name [-c] CLUSTER-NAME \
    --resource-group [-g] RESOURCE-GROUP \
    --identity
```

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
