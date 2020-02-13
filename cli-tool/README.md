# `hub-manager`

`hub-manager` is a CLI tool that will interact with Hub23 deployed on Azure.

## Installation

It is recommended to use Python version 3.7 with `hub-manager`.

```bash
# Clone the repo
git clone https://github.com/alan-turing-institute/hub23-deploy.git
# Change to the cli-tool directory
cd hub23-deploy/cli-tool
# Install the CLI
python setup.py install
# Test the CLI by calling the help message
hub-manager --help
```

## Usage

`hub-manager` can be called to run one of four actions.

### Generate the Configuration Files

```bash
hub-manager generate-config-files
```

This action will pull secrets from the Azure Key Vault, populate `hub23-deploy/deploy/prod-template.yaml` and save the output as `hub23-deploy/.secret/prod.yaml`.

### Get Logs

```bash
hub-manager get-logs
```

The action will print the logs of the JupyterHub pod to the console.

You can instead pull the logs of the Binder pod by providing the `--pod binder` argument.

```bash
hub-manager get-logs --pod binder
```

### Print Pods

```bash
hub-manager print-pods
```

This action will print the status of all running Kubernetes pods to the console.

### Upgrade the Helm Chart

```bash
hub-manager helm-upgrade
```

This action will upgrade the helm chart deployed to the Kubernetes cluster by calling [`generate-config-files`](#generate-the-configuration-files).

#### Optional flags for `helm-upgrade`

- `--dry-run`: Performs a dry run of the helm chart upgrade
- `--debug`: Activates debugging output for the helm upgrade

### Global Flags

- `--verbose/-v`: Outputs logs to the console
- `--identity`: Allows the script to login to Azure using a Managed System Identity
