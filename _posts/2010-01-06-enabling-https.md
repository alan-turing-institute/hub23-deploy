---
layout: page
share: false
title: "Enabling HTTPS using `cert-manager`"
---

This document will walk through the steps required to enable HTTPS on Hub23 using [`cert-manager`](https://docs.cert-manager.io/en/latest/).
It assumes you have deployed Hub23 using a local helm chart as outlined in ["Installing BinderHub with a Local Helm Chart"]({{ site.baseurl }}{% post_url 2010-01-07-installing-binderhub-local-helm-chart %}) and created a subdomain as per ["Enabling Page Redirection"]({{ site.baseurl }}{% post_url 2010-01-12-enabling-page-redirection %}).

The following documentation is based on [this WIP documentation](https://discourse.jupyter.org/t/wip-documentation-about-cert-manager/2068).

## Table of Contents

- [Context](#context)
  - [How `cert-manager` works](#how-cert-manager-works)
- [Setting up files](#setting-up-files)
  - [Create `templates/cluster-issuer.yaml`](#create-templatesclusterissueryaml)
  - [Create `deploy/cert-manager.yaml`](#create-deploycertmanageryaml)
- [Installation](#installation)

---

## Context

To setup secure HTTPS communication, we need to have a _certificate_ associated with our _domain_ from a _Certificate Authority_ (CA).
Thankfully, there's [Let's Encrypt](https://letsencrypt.org/) which is a widely trusted CA that is also free to request certificates from.

But CA's don't jkust give away certificates.
They require proof of domain ownership through a _challenge_.
This is technically cumbersone and often automated by services like [`kube-lego`](https://github.com/jetstack/kube-lego) and [`cert-manager`](https://github.com/jetstack/cert-manager).

**HTTPS vs TLS**<br>
_HTTPS_ is the secured version of HTTP: HyperText Transfer Protocol.
HTTP is the protocol used by browsers and web servers to communicate and exchange information.
When that exchange of data is encrypted with SSL/_TLS_, then we call it _HTTPS_.
The S stands for Secure.
{: .notice--accent}

TLS termination, the transition from encrypted to unencrypted traffic, can be done in various locations.
A common place in the world of Kubernetes is to let this be managed by ingress controllers.
An ingress controller is something that acts to make Kubernetes ingress resources come to life.
It is possible to use an ingress controller made available by your cloud provider or one that you have hosted yourself within the cluster, such as [`nginx-ingress`](https://github.com/helm/charts/tree/master/stable/nginx-ingress).

Below is a guide on how to use `cert-manager` along with `nginx-ingress` to enable HTTPS.
Both of these can be installed as Helm Charts.

### How `cert-manager` works

`cert-manager` looks at [Kubernetes ingress resources](https://kubernetes.io/docs/concepts/services-networking/ingress/).
For each ingress resource it finds, it further looks for annotations attached this resource.
If the ingress resource has an annotation that indicates `cert-manager` needs to take action, then it will try to provide a certificate from Let's Encrypt.

An example of an annotation indicating the resource requires a certificate and `cert-manager` should request one looks as follows:

```yaml
kubernetes.io/tls-acme: "true"
```

If it decides action is required, `cert-manager` will further look at the ingress object.
What hosts or domains does it want to handle traffic to?
From what Kubernetes secret resource does it want to read the certificate from?
It will combine this information with any default settings such as what _Issuer_ to use.

An _Issuer_ is a `cert-manager` concept.
It describes what CA to speak with, what email to use as a contact person, and what kind of challenge to use.
This can be configured in `cert-manager`'s helm chart values like so:

```yaml
# Example configuration of cert-manager default values
# for requesting certificates
cert-manager:
  ingressShim:
    defaultIssuerName: "a-manually-created-issuer-resource"
    defaultIssuerKind: "Issuer"
    defaultACMEChallengeType: "http01"
```

## Setting up files

Some extra files are required which we will outline below.

The resulting file structure will look as follows:

```bash
hub23-chart/
|-files/
|-templates/
| |-clusterissuer.yaml
| |-user-configmap.yaml
|
|-Chart.yaml
|-requirements.yaml
|-values.yaml
```

We will have already created `Chart.yaml`, `requirements.yaml` and `values.yaml` in ["Installing BinderHub with a Local Helm Chart"]({{ site.baseurl }}{% post_url 2010-01-07-installing-binderhub-local-helm-chart %}).

### Create `templates/cluster-issuer.yaml`

```yaml
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: hub23registry@turing.ac.uk
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: hub23registry@turing.ac.uk
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Create `deploy/cert-manager.yaml`

```yaml
ingressShim:
  defaultIssuerName: letsencrypt-prod
  defaultIssuerKind: ClusterIssuer
```

## Installation using Helm v3

#### 1. Create a namespace for `cert-manager`

```bash
kubectl create namespace cert-manager
```

#### 2. Add the `cert-manager` chart repo to Helm

```bash
helm3 repo add jetstack https://charts.jetstack.io
helm3 repo update
```

#### 3. Install the Custom Resource Definitions

```bash
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v1.0.3/cert-manager.crds.yaml
```

#### 4. Install using Helm

```bash
helm3 install cert-manager jetstack/cert-manager \
    --version v1.0.3 \
    --namespace cert-manager \
    -f deploy/cert-manager.yaml
```
