---
layout: page
share: false
title: "Setup Helm"
---

This documentation will walk through setting up Helm on the Kubernetes cluster.

We assume you have the following CLI installed:

- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm)

## Table of Contents

- [Setting up Helm](#setting-up-helm)

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

**NOTE:** If you install `helm` on another computer to access the same cluster, you will not need to run this step again, instead run the following. `helm init --client-only`
{: .notice--info}

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

**NOTE:** If the versions do not match, run the following commands and check the versions again. `helm init --upgrade`
{: .notice--info}
