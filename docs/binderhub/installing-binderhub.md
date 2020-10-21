(content:binderhub:direct-chart)=
# Installing BinderHub directly from the Helm Chart

## Downloading the Required Secrets

To set up the BinderHub, we will need to download the API and secret tokens from the keyvault like so:

```bash
az keyvault secret download --vault-name hub23-keyvault --name apiToken --file .secret/apiToken.txt
```

```bash
az keyvault secret download --vault-name hub23-keyvault --name secretToken --file .secret/secretToken.txt
```

## Create a `secret.yaml` file

In the `deploy/` folder, create a `secret-template.yaml` file with the following layout.

```yaml
jupyterhub:
  hub:
    services:
      binder:
        apiToken: "{apiToken}"
  proxy:
    secretToken: "{secretToken}"
```

We can then use [`sed`](http://www.grymoire.com/Unix/Sed.html) to insert the API and secret tokens.

```bash
sed -e "s/{apiToken}/$(cat .secret/apiToken.txt)/" \
    -e "s/{secretToken}/$(cat .secret/secretToken.txt)/" \
    deploy/secret-template.yaml > .secret/secret-template.yaml
```

### Deleting local copies of the secret files

Once you have constructed `.secret/secret.yaml`, you should delete the local copies of the API and secret tokens.

```bash
rm .secret/apiToken.txt
rm .secret/secretToken.txt
```

## Connect a Container Registry

We need to attach a Container Registry to the BinderHub so that it has a place to push built images to.
See {ref}`content:binderhub:connect-container-registry` for how to do that.

## Create a `config.yaml` file

Again in the `deploy` folder, create a `config.yaml` file with the following format.

```yaml
config:
  BinderHub:
    use_registry: true
    image_prefix: "YOUR_PREFIX_HERE"
```

The image prefix should take the following form:

```bash
{ container registry username }-{ identifier to prepend to image name }-
```

## Pull the Helm Charts for JupyterHub/BinderHub

This command will add the repository of JupyterHub/BinderHub Helm Charts to your package manager.

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update
```

## Install the latest release of the BinderHub Chart

As of 2019-10-16, the most recent BinderHub Helm chart was `0.2.0-a2079a5`.
Find the most recent version [here](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).
Install the Chart with the following command.
This will install both a JupyterHub and a BinderHub.

```bash
helm install jupyterhub/binderhub \
    --version=0.2.0-a2079a5 \
    --name hub23 \
    --namespace hub23 \
    --create-namespace \
    -f .secret/secret.yaml \
    -f deploy/config.yaml \
    --cleanup-on-fail
```

`--name` and `--namespace` don't strictly have to match, but it makes it easier to remember if they do.
They should also only contain lowercase alphanumerical characters or hyphens (`-`).

## Connect JupyterHub and BinderHub

Get the External IP of the JupyterHub by running the following command.
It may take some time to update, so keep running the command until `<pending>` disappears.

```bash
kubectl get svc proxy-public --namespace hub23
```

Once you have the External IP address, update `deploy/config.yaml` to look like the following.

```yaml
config:
  BinderHub:
    use_registry: true
    image_prefix: "IMAGE_PREFIX"
    hub_url: "http://<IP in EXTERNAL IP>"
```

Upgrade the Helm Chart to deploy the change.

```bash
helm upgrade hub23 jupyterhub/binderhub \
    --version=0.2.0-a2079a5 \
    -f .secret/secret.yaml \
    -f deploy/config.yaml \
    --cleanup-on-fail
```

## Finally, get the IP address for the Binder page

The External IP address from this command will be the IP address of the Binder page.

```bash
kubectl get svc binder --namespace hub23
```

Check the deployment is working by launching a repo, e.g.: <https://github.com/binder-examples/requirements>
