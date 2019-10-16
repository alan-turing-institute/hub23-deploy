# Installing BinderHub

This document walks through the steps required to install Hub23 (the Turing hosted BinderHub).

We assume you have the following CLI's installed:

- [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm)

Table of Contents:

- [Setting up Helm](#setting-up-helm)
- [Installing a BinderHub](#installing-a-binderhub)
- [Increasing GitHub API limit](#increasing-github-api-limit)

---

## Setting up Helm

Helm is a package manager for Kubernetes and is used for installing, managing and upgrading applications on the cluster.
Helm has two parts: a local client (`helm`) and a remote server (`tiller`).
When running `helm` commands in your local terminal, a message is relayed to `tiller` which executes the command across the remote cluster.
Helm is used to deploy apps using Charts.
Charts are a collection of information on how to install software and acts as a templating engine.
A Helm Chart will populate various configuration files with the required info and wraps the `kubectl apply` command to install/upgrade the package.

#### 1. Setup a ServiceAccount for `tiller`

When you (a human) accesses your Kubernetes cluster, you are authenticated as a particular User Account.
Processes in containers running in pods are authenticated as a particular Service Account.
More details [here](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/).

```bash
kubectl --namespace kube-system create serviceaccount tiller
```

#### 2. Give ServiceAccount permissions to manage the cluster

This step enables Role Based Access Control (RBAC) so Kubernetes can secure which pods/users can perform what kind of actions on the cluster.
If RBAC is disabled, all pods are given root equivalent permission on all the Kubernetes nodes and the cluster itself.
This can leave the cluster vulnerable to attacks.
See [Project Jupyter's docs](https://zero-to-jupyterhub.readthedocs.io/en/latest/security.html#use-role-based-access-control-rbac) for more details.

```bash
kubectl create clusterrolebinding tiller \
    --clusterrole cluster-admin \
    --serviceaccount=kube-system:tiller
```

#### 3. Initialise `helm` and `tiller`

This step will create a `tiller` deployment in the kube-system namespace and set-up your local `helm` client.
This is the command that connects your remote Kubernetes cluster to the commands you execute in your local terminal and only needs to be run once per Kubernetes cluster.

```bash
helm init --service-account tiller --wait
```

If you install `helm` on another computer to access the same cluster, you will not need to run this step again, instead run the following.

```bash
helm init --client-only
```

#### 4. Secure Helm against attacks from within the cluster

`tiller`s port is exposed in the cluster without authentication and if you probe this port directly (i.e. by bypassing `helm`) then `tiller`s permissions can be exploited.
This step forces `tiller` to listen to commands from localhost (i.e. `helm`) _only_ so that e.g. other pods inside the cluster cannot ask `tiller` to install a new chart.
For example, this could give other pods arbitrary, elevated privileges to exploit.
More details [here](https://engineering.bitnami.com/articles/helm-security.html).

```bash
kubectl patch deployment tiller-deploy \
    --namespace=kube-system \
    --type=json \
    --patch='[{
      "op": "add",
      "path": "/spec/template/spec/containers/0/command",
      "value": ["/tiller", "--listen=localhost:44134"]
    }]'
```

#### 5. Verify the installation

To verify the correct versions have been installed properly, run the following command.

```bash
helm version
```

You must have at least version 2.11.0 and the client (`helm`) and server (`tiller`) versions must match.
The server may take a little while to appear.

If the version do not match, run the following commands and check the versions again.

```bash
helm init --upgrade
```

## Installing a BinderHub

#### 1. Create a `secret.yaml` file

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

#### Deleting local copies of the secret files

Once you have constructed `.secret/secret.yaml`, you should delete the local copies of the API and secret tokens.

```bash
rm .secret/apiToken.txt
rm .secret/secretToken.txt
```

#### 1a. Connecting with DockerHub

Add the following to `.secret/secret.yaml`, where `{docker-id}` if your ID (not the associated e-mail address).
This account **must** be a member of the `binderhubtest` DockerHub organisation.

```bash
registry:
  username: {docker-id}
  password: {password}
```

As in the above step, you could use `sed` to input these variables.

#### 1b. Connecting with an Azure Container Registry (ACR)

See [`docs/03-create-azure-container-registry.md`](03-create-azure-container-registry.md).

#### 2. Create a `config.yaml` file

Again in the `deploy` folder, create a `config.yaml` file with the following format.

```yaml
config:
  BinderHub:
    use_registry: true
    image_prefix: binderhubtest/hub23-dev-
```

`hub23-dev-` will be prepended to the Docker images of the binder repos that are pushed to the DockerHub organisation `binderhubtest`.

#### 3. Pull the Helm Charts for JupyterHub/BinderHub

This command will add the repository of JupyterHub/BinderHub Helm Charts to your package manager.

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update
```

#### 4. Install the latest release of the BinderHub Chart

As of 2019-10-16, the most recent BinderHub Helm chart was `0.2.0-a2079a5`.
Find the most recent version [here](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).
Install the Chart with the following command.
This will install both a JupyterHub and a BinderHub.

```bash
helm install jupyterhub/binderhub \
    --version=0.2.0-a2079a5 \
    --name hub23 \
    --namespace hub23 \
    -f .secret/secret.yaml \
    -f deploy/config.yaml
```

`--name` and `--namespace` don't strictly have to match, but it makes it easier to remember if they do.
They should also only contain lowercase alphanumerical characters or hyphens (`-`).

#### 5. Connect JupyterHub and BinderHub

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
    image_prefix: binderhubtest/hub23-dev-
    hub_url: http://<IP in EXTERNAL IP>
```

Upgrade the Helm Chart to deploy the change.

```bash
helm upgrade hub23 jupyterhub/binderhub \
    --version=0.2.0-a2079a5 \
    -f .secret/secret.yaml \
    -f deploy/config.yaml
```

#### 6. Finally, get the IP address for the Binder page

The External IP address from this command will be the IP address of the Binder page.

```bash
kubectl get svc binder --namespace hub23
```

Check the deployment is working by launching a repo, e.g.: <https://github.com/binder-examples/requirements>

## Increasing GitHub API limit

**N.B.:** This step is not strictly necessary though is recommended before sharing the Binder link with others.

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

Update `deploy/secret-template.yaml` with the following.

```yaml
jupyterhub:
  config:
    GitHubRepoProvider:
      access_token: {accessToken}
```

Again, we can use `sed` to populate this secret:

```bash
sed -e "s/{accessToken}/$(cat .secret/accessToken.txt)/" \
    deploy/secret-template.yaml > .secret/secret.yaml
```

#### Delete the local copy

Remember to delete the local copy after populating `.secret/secret.yaml`.

```bash
rm .secret/accessToken.txt
```

#### 4. Upgrade the `helm` chart

Upgrade the `helm` chart to roll out the change to the BinderHub.

```bash
helm upgrade hub23 jupyterhub/binderhub \
    --version=0.2.0-<commit-hash> \
    -f .secret/secret.yaml \
    -f deploy/config.yaml
```

Here, `<commit-hash>` can be the most recent Helm Chart version.
