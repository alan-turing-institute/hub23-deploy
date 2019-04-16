# Deploy a BinderHub on the Turing's Azure subscription

This document walks through the steps required to deploy Hub23 (the Turing hosted BinderHub) onto the Turing's Azure subscription.

We assume you have the following CLI's installed:
* [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
* [Kubernetes CLI (`kubectl`)](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
* [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm)

## Setup

#### 1. Login to Azure

```
az login --output none
```

Login with your Turing account.

#### 2. Activate the Subscription

Hub23 has its own subscription and so we have to activate that.

To check which subscriptions you have access to, run the following:

```
az account list --refresh --output table
```

You should see `Turing-BinderHub` listed as an option.
If not, request access by opening a TopDesk ticket.

To activate the subscription, run the following:

```
az account set -s Turing-BinderHub
```

#### 3. Create a Resource Group

Azure groups related resources together by assigning them a Resource Group.
We need to create one for Hub23.

```
az group create --name Hub23 --location westeurope --output table
```

* `--name` is what we'll use to identify resources relating to the BinderHub and should be short and descriptive.
  Hence we've given it the same name as our hub.
* `--location` sets the [data centre](https://azure.microsoft.com/en-gb/global-infrastructure/locations/) that will host the resources.
* `--output table` prints the info in a human-readable format.

**N.B.:** If you have already followed the docs on creating a key vault, then this resource group should already exist and this step can be skipped.

## Download the required secrets

We will require some info from the key vault in order to deploy the Kubernetes cluster and the BinderHub.

#### 1. Create a secrets folder

Create a folder in which to download the secrets so.
This will be git-ignored.

```
mkdir .secret
```

#### 2. Download the secrets

We will require the following secrets:
* Service Principal app ID and key
* public SSH key
* API and secret tokens

They should be downloaded to files in the `.secret` folder so that they are git-ignored.

Download the Service Principal:

```
az keyvault secret download --vault-name hub23-keyvault --name SP-appID --file .secret/appID.txt
```

```
az keyvault secret download --vault-name hub23-keyvault --name SP-key --file .secret/key.txt
```

Download the public SSH key:

```
az keyvault secret download --vault-name hub23-keyvault --name ssh-key-Hub23cluster-public --file .secret/ssh-key-hub23cluster.pub
```

Download the API and secret tokens:

```
az keyvault secret download --vault-name hub23-keyvault --name apiToken --file .secret/apiToken.txt
```

```
az keyvault secret download --vault-name hub23-keyvault --name secretToken --file .secret/secretToken.txt
```

## Set up for Autoscaling

See the following docs:
* https://docs.microsoft.com/en-us/azure/aks/cluster-autoscaler
* https://docs.microsoft.com/en-us/azure/aks/upgrade-cluster

#### 1. Install aks-preview CLI extension

```
az extension add --name aks-preview
```

#### 2. Register scale set feature provider

```
az feature --name VMSSPreview --namespace Microsoft.ContainerService
```

This will take a while to register.
Run the following command to check the status.

```
az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/VMSSPreview')].{Name:name,State:properties.state}"
```

#### 3. Refresh the registration

```
az provider register --namespace Microsoft.ContainerService
```

## Create the Kubernetes cluster

#### 1. Create the AKS cluster

The following command will deploy a Kubernetes cluster into the Hub23 resource group.
This command has been known to take between 7 and 30 minutes to execute depending on resource availability in the location we set when creating the resource group.

```
az aks create \
    --resource-group Hub23 \
    --name hub23cluster \
    --kubernetes-version 1.12.7 \
    --node-count 3 \
    --enable-vmss \
    --enable-cluster-autoscaler \
    --min-count 3 \
    --max-count 6 \
    --ssh-key-value .secret/ssh-key-hub23cluster.pub \
    --service-principal $(cat .secret/appID.txt) \
    --client-secret $(cat .secret/key.txt) \
    --output table
```

* `--node-count` is the number of nodes to be deployed. 3 is recommended for a stable, scalable cluster.
* `--kubernetes-version` needs to be 1.12.4 or greater to be compatible with the cluster autoscaler.
* `--enable-vmss` enables the Virtual Machine Scale Set of scalable VMs.
* `--min-count`/`--max-count` defines the minimum and maximum number of nodes to be spun up/down.

#### Delete local copies of the secret files

Once the Kubernetes cluster is deployed, you should delete the local copy of the Service Principal and public SSH key.

```
rm .secret/ssh-key-hub23cluster.pub
rm .secret/appID.txt
rm .secret/key.txt
```

#### 2. Get credentials for `kubectl`

We need to configure the local installation of the Kubernetes CLI to work with the version deployed onto the cluster, and do so with the following command.

```
az aks get-credentials --name hub23cluster --resource-group Hub23 --output table
```

This command would need to be repeated when trying to manage the cluster from another computer or if you have been working with a different cluster.

#### 3. Check the cluster is fully functional

Output the status of the nodes.

```
kubectl get node
```

All three nodes should have `STATUS` as `Ready`.

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

```
kubectl --namespace kube-system create serviceaccount tiller
```

#### 2. Give ServiceAccount permissions to manage the cluster

This step enables Role Based Access Control (RBAC) so Kubernetes can secure which pods/users can perform what kind of actions on the cluster.
If RBAC is disabled, all pods are given root equivalent permission on all the Kubernetes nodes and the cluster itself.
This can leave the cluster vulnerable to attacks.
See [Project Jupyter's docs](https://zero-to-jupyterhub.readthedocs.io/en/latest/security.html#use-role-based-access-control-rbac) for more details.

```
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
```

#### 3. Initialise `helm` and `tiller`

This step will create a `tiller` deployment in the kube-system namespace and set-up your local `helm` client.
This is the command that connects your remote Kubernetes cluster to the commands you execute in your local terminal and only needs to be run once per Kubernetes cluster.

```
helm init --service-account tiller --wait
```

If you install `helm` on another computer to access the same cluster, you will not need to run this step again, instead run the following.

```
helm init --client-only
```

#### 4. Secure Helm against attacks from within the cluster

`tiller`s port is exposed in the cluster without authentication and if you probe this port directly (i.e. by bypassing `helm`) then `tiller`s permissions can be exploited.
This step forces `tiller` to listen to commands from localhost (i.e. `helm`) _only_ so that e.g. other pods inside the cluster cannot ask `tiller` to install a new chart.
For example, this could give other pods arbitrary, elevated privileges to exploit.
More details [here](https://engineering.bitnami.com/articles/helm-security.html).

```
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

```
helm version
```

You must have at least version 2.11.0 and the client (`helm`) and server (`tiller`) versions must match.

## Installing a BinderHub

#### 1. Create a `secret.yaml` file

In the `.secret/` folder so that it will be git-ignored, create a `secret.yaml` file with the following layout.

```
jupyterhub:
  hub:
    services:
      binder:
        apiToken: "<apiToken>"
  proxy:
    secretToken: "<secretToken>"
```

We can then use [`sed`](http://www.grymoire.com/Unix/Sed.html) to insert the API and secret tokens.

```
sed -e "s/<apiToken>/$(cat .secret/apiToken.txt)/" -e "s/<secretToken>/$(cat .secret/secretToken.txt)/" -i .secret/secret.yaml
```

#### a. Connecting with DockerHub

Add the following to `.secret/secret.yaml`, where `<docker-id>` if your ID (not the associated e-mail address).
This account **must** be a member of the `binderhubtest` DockerHub organisation.

```
registry:
  username: <docker-id>
  password: <password>
```

As in the above step, you could use `sed` to input these variables.

#### 2. Create a `config.yaml` file

Again in the `.secret/` folder, create a `config.yaml` file with the following format.

```
config:
  BinderHub:
    use_registry: true
    image_prefix: binderhubtest/hub23-dev-
```

`hub23-dev-` will be prepended to the Docker images of the binder repos that are pushed to the DockerHub organisation `binderhubtest`.

#### 3. Pull the Helm Charts for JupyterHub/BinderHub

This command will add the repository of JupyterHub/BinderHub Helm Charts to your package manager.

```
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update
```

#### Deleting local copies of the secret files

Once you have constructed `.secret/secret.yaml` and `.secret/config.yaml`, you should delete the local copies of the API and secret tokens.

```
rm .secret/apiToken.txt
rm .secret/secretToken.txt
```

#### 4. Install the latest release of the BinderHub Chart

As of 2019-03-20, the most recent BinderHub Helm chart was `0.2.0-3b53fce`.
Find the most recent version [here](https://jupyterhub.github.io/helm-chart/#development-releases-binderhub).
Install the Chart with the following command.
This will install both a JupyterHub and a BinderHub.

```
helm install jupyterhub/binderhub --version=0.2.0-3b53fce --name=hub23 --namespace=hub23 -f .secret/secret.yaml -f .secret/config.yaml
```

`--name` and `--namespace` don't strictly have to match, but it makes it easier to remember if they do.
They should also only contain lowercase alphanumerical characters or hyphens (`-`).

#### 5. Connect JupyterHub and BinderHub

Get the External IP of the JupyterHub by running the following command.
It may take some time to update, so keep running the command until `<pending>` disappears.

```
kubectl --namespace=hub23 get svc proxy-public
```

Once you have the External IP address, update `.secret/config.yaml` to look like the following.

```
config:
  BinderHub:
    use_registry: true
    image_prefix: binderhubtest/hub23-dev-
    hub_url: http://<IP in EXTERNAL IP>
```

Update the Helm Chart to deploy the change.

```
helm upgrade hub23 jupyterhub/binderhub --version=0.2.0-3b53fce -f .secret/secret.yaml -f .secret/config.yaml
```

#### 6. Finally, get the IP address for the Binder page

The External IP address from this command will be the IP address of the Binder page.

```
kubectl --namespace=hub23 get svc binder
```

Check the deployment is working by launching a repo, e.g.: https://github.com/binder-examples/requirements

## Enabling Autoscaling

We need to enforce an autoscaling rule in the [Azure Portal](https://portal.azure.com/).

#### 1. Registering Subscription with Microsoft.Insights

On the first attempt to configure an autoscaling rule for the Virtual Machine Scale Set, it was denied as the active subscription was not registed to use "Microsoft.Insights"
This allows use of the "Monitoring" options in Azure - most usefully the Metrics so we can watch how much CPU etc. the BinderHub is using.

The following command will register Microsoft.Insights for use on the active subscription.

```
az provider register --namespace microsoft.insights
```

To check the status of the registration, run the following command.

```
az provider show -n microsoft.insights
```

#### 2. Setting an Autoscaling Rule

Under "Resources" on the "Turing-BinderHub" subscription blade, select the Virtual Machine Scale Set.
It should be named something like "aks-nodepool1-<random-number>-vmss".

<html><img src="figures/select-vmss.png" alt="select-vmss" height="504" width="999"></html>

From the left hand side menu, select "Scaling".

<html><img src="figures/select-scaling.png" alt="select-scaling" height="504" width="999"></html>

Click the blue "Enable autoscaling" button and an auto-generated form will appear.
We will add a rule that will add 1 new instance (or node) when the average CPU usage over a 10 minute period is greater than 70%.

Make sure the "Scale based on metric" option is selected and then select "+ Add new rule".
This will pop up a pre-filled rule form for 70% average CPU usage over a 10 minute period.
Double check this form, but I didn't change any of the defaults.

Save and configure this rule.

<html><img src="figures/set-autoscaling-rule.png" alt="set-autoscaling-rule" height="504" width="999"></html>

## Assigning labels to nodes

We will label the three core nodes and add a Node Affinity to the `config.yaml` file in order to keep the core Pods on the core nodes.

See the following docs:
* https://zero-to-jupyterhub.readthedocs.io/en/latest/reference.html#scheduling-corepods

#### 1. Label the 3 minimum nodes as system nodes

Use the following command to get the names of the 3 core nodes.

```
kubectl get nodes
```

Label each node with a `node-purpose=system` label as follows.

```
kubectl label nodes <node-name> hub.jupyter.org/node-purpose=core
```

#### 2. Update `config.yaml` with Node Affinity setting

Add the following to `config.yaml`.

```
jupyterhub:
  scheduling:
        # match core pods to nodes with label 'hub.jupyter.org/node-purpose=core'
    corePods:
      nodeAffinity:
        # matchNodePurpose valid options:
        # - ignore
        # - prefer (the default)
        # - require
        matchNodePurpose: require
```