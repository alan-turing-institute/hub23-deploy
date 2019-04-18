# hub23-deploy

A repo to manage the private Turing BinderHub instance, Hub23.

## Requirements

Three command line interfaces are used to manage Hub23:

* [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) - to manage the Azure compute resources
* [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl) - to manage the Kubernetes cluster
* [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm) - to manage the BinderHub application running on the Kubernetes cluster

## Usage

`make-config-files.sh` is a shell script to automatically recreate the configuration files in order to maintain or upgrade Hub23.

```
chmod 700 make-config-files.sh
./make-config-files.sh
```

This will populate `secret-template.yaml` and `config-template.yaml` (using [`sed`](http://www.grymoire.com/Unix/Sed.html)) with the appropriate information and save the output as `.secret/secret.yaml` and `.secret/config.yaml`. It will ask for your Docker ID and password and your account must be a member of the DockerHub organisation `binderhubtest`.

`.secret/` is a git-ignored folder so that the `secret.yaml` and `config.yaml` files (and any secrets downloaded in the process of creating them) cannot be pushed to GitHub.

Lastly, the script will print the Binder IP address.

## Maintaining or Upgrading Hub23

If changes are made to `.secret/secret.yaml` and/or `.secret/config.yaml` during development, make sure that:
* the new format is reflected in `secret-template.yaml` and/or `config-template.yaml` and any new secrets/tokens/passwords are redacted;
* new secrets/tokens/passwords are added to the Azure key vault (see `docs/azure-keyvault.md`);
* `make-config-files.sh` is updated in order to populate the templates with the appropriate information (i.e. using `sed`).

This will ensure that a future developer (someone else or future-you!) can recreate the configuration files for Hub23.

To upgrade the BinderHub Helm Chart:
```
helm upgrade hub23 jupyterhub/binderhub --version=0.2.0-<commit-hash> -f .secret/secret.yaml -f .secret/config.yaml
```
where `<commit-hash>` can be found [here](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).

Please try to keep track of the deployed `<commit-hash>` [below](#changelog).

## Useful commands

To print the IP address of the Binder page:
```
kubectl --namespace=hub23 get svc binder
```

To access the JupyterHub logs:
```
# Print the running pods, find the one that begins with "hub-"
kubectl get pods --namespace hub23
kubectl logs hub-<random-string> --namespace hub23
```

<a name="changelog"></a>
## Changelog

A record of the latest BinderHub Chart version deployed (reverse chronological order).

* 
* 2019-04-16: `0.2.0-1eac3a0`
* 2019-03-22: `0.2.0-3b53fce`
