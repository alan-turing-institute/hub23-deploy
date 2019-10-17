# Enabling HTTPS using `cert-manager`

This document will walk through the steps required to enable HTTPS on Hub23 using [`cert-manager`](https://docs.cert-manager.io/en/latest/).
It assumes you have deployed Hub23 using a local helm chart as outlined in [`docs/03ii-installing-binderhub-local-helm-chart.md`](03ii-installing-binderhub-local-helm-chart.md) and created a subdomain as per [docs/08-enabling-page-redirection.md](08-enabling-page-redirection.md).

The following documentation is based on [this WIP documentation](https://discourse.jupyter.org/t/wip-documentation-about-cert-manager/2068).

Table of Contents:

- [Setting up files](#setting-up-files)
  - [Create `templates/clusterisuuer.yaml`](#create-templatesclusterisuueryaml)
  - [Create `templates/user-configmap.yaml`](#create-templatesuser-configmapyaml)
  - [Create `templates/_helpers.tpl`](#create-templates_helperstpl)
  - [Create `files/etc/jupyter/templates/login.html`](#create-filesetcjupytertemplatesloginhtml)
  - [Create `files/etc/jupyter/templates/page.html`](#create-filesetcjupytertemplatespagehtml)
  - [Create `files/etc/jupyter/jupyter_notebook_config.py`](#create-filesetcjupyterjupyter_notebook_configpy)
- [Installation](#installation)

---

## Setting up files

Some extra files are required which we will outline below.

The resulting file structure will look as follows:

```bash
hub23-chart/
|-files/
| |-etc/
| | |-jupyter/
| | | |-templates/
| | | | |-login.html
| | | | |-page.html
| | | |
| | | |-jupyter_notebook_config.py
|
|-templates/
| |-clusterissuer.yaml
| |-user-configmap.yaml
| |-_helpers.tpl
|
|-Chart.yaml
|-requirements.yaml
|-values.yaml
```

We will have already created `Chart.yaml`, `requirements.yaml` and `values.yaml` in [`docs/03ii-installing-binderhub-local-helm-chart.md`](03ii-installing-binderhub-local-helm-chart.md).

### Create `templates/clusterisuuer.yaml`

```yaml
---
apiVersion: certmanager.k8s.io/v1alpha1
kind: ClusterIssuer
metadata:
  name: prod
  labels:
    helm.sh/chart: {{ include "hub23-chart.chart" . }}
    app.kubernetes.io/name: {{ include "hub23-chart.name" . }}
    app.kubernetes.io/managed-by: {{ .Release.Service }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: {{ .Values.letsencrypt.contactEmail }}
    privateKeySecretRef:
      name: prod-acme-key
    http01: {}
---
apiVersion: certmanager.k8s.io/v1alpha1
kind: ClusterIssuer
metadata:
  name: staging
  labels:
    helm.sh/chart: {{ include "hub23-chart.chart" . }}
    app.kubernetes.io/name: {{ include "hub23-chart.name" . }}
    app.kubernetes.io/managed-by: {{ .Release.Service }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: {{ .Values.letsencrypt.contactEmail }}
    privateKeySecretRef:
      name: staging-acme-key
    http01: {}
```

### Create `templates/user-configmap.yaml`

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: user-etc-jupyter
  labels:
    app: jupyterhub
    component: etc-jupyter
    heritage: {{ .Release.Service }}
    release: {{ .Release.Name }}

data:
  {{- range $name, $content := .Values.etcJupyter }}
  {{- if eq (typeOf $content) "string" }}
  {{ $name }}: |
    {{- $content | nindent 4 }}
  {{- else }}
  {{ $name }}: {{ $content | toJson | quote }}
  {{- end }}
  {{- end }}
  {{- (.Files.Glob "files/etc/jupyter/*").AsConfig | nindent 2 }}
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: user-etc-jupyter-templates
  labels:
    app: jupyterhub
    component: etc-jupyter
    heritage: {{ .Release.Service }}
    release: {{ .Release.Name }}
data:
  {{- (.Files.Glob "files/etc/jupyter/templates/*").AsConfig | nindent 2 }}
```

### Create `templates/_helpers.tpl`

```yaml
{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "hub23-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hub23-chart.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hub23-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}
```

### Create `files/etc/jupyter/templates/login.html`

```html
{% extends "templates/login.html" %}
{% block site %}

<div id="ipython-main-app" class="container">
  <h1>Binder inaccessible</h1>
  <h2>
    You can get a new Binder for this repo by clicking <a href="{{binder_url}}">here</a>.
  </h2>
  <p>
    The shareable URL for this repo is: <tt>{{binder_url}}</tt>
  </p>

  <h4>Is this a Binder that you created?</h4>
  <p>
    If so, your authentication cookie for this Binder has been deleted or expired.
    You can launch a new Binder for this repo by clicking <a href="{{binder_url}}">here</a>.
  </p>

  <h4>Did someone give you this Binder link?</h4>
  <p>
    If so, the link is outdated or incorrect.
    Recheck the link for typos or ask the person who gave you the link for an updated link.
    A shareable Binder link should look like <tt>{{binder_url}}</tt>.
</div>
{% endblock site %}
```

### Create `files/etc/jupyter/templates/page.html`

```html
{% extends "templates/page.html" %}
{% block login_widget %}{% endblock %}
```

### Create `files/etc/jupyter/jupyter_notebook_config.py`

```python
import os
c.NotebookApp.extra_template_paths.append('/etc/jupyter/templates')
c.NotebookApp.jinja_template_vars.update({
    'binder_url': os.environ.get('BINDER_URL', 'https://mybinder.org'),
})
```

## Installation

#### 1. Add `nginx-ingress` and `cert-manager` dependencies to `requirements.yaml`

Check the repos (in comments) for the most up-to-date version.

```yaml
dependencies:
  # https://github.com/helm/charts/tree/master/stable/nginx-ingress
  - name: nginx-ingress
    version: "1.19.0"
    repository: "https://kubernetes-charts.storage.googleapis.com"
  # https://github.com/helm/charts/tree/master/stable/cert-manager
  - name: cert-manager
    version: "v0.10.0"
    repository: "https://charts.jetstack.io"
```

#### 2. Add the repos to the local helm manager

```bash
helm repo add cert-manager https://charts.jetstack.io
```

#### 3. Install `cert-manager`'s Custom Resource Definitions (CRDs)

```bash
kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.10/deploy/manifests/00-crds.yaml
```

#### 4. Add your desired email address for communication with LetsEncrypt to `values.yaml`

```yaml
letsencrypt:
  contactEmail: YOUR-EMAIL@WHATEVER.COM
```

#### 4. Perform a helm upgrade

This first upgrade will install the dependencies without affecting the cluster.

```bash
cd hub23-chart && helm dependency update && cd ..
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml
```

#### 5. Install `nginx-ingress` and `cert-manager` defaults into `vaules.yaml`

We will start with the "staging" issuer to test the system.

```yaml
nginx-ingress:
  controller:
    config:
      proxy-body-size: 64m

cert-manager:
  ingressShim:
    defaultIssuerName: "staging"
    defaultIssuerKind: "ClusterIssuer"
    defaultACMEChallengeType: "http01"
```

#### 6. Perform another helm upgrade

```bash
cd hub23-chart && helm dependency update && cd ..
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml
```

#### 7. Enable ingress, annotations, hosts and TLS for the JupyterHub and Binder in `values.yaml`

```yaml
binderhub:
  ingress:
    enabled: true
    annotations:
      # cert-manager provides a TLS secret
      # This will ask cert-manager to be configured with default values. It's better to configure default values.
      kubernetes.io/tls-acme: "true"
      # nginx-ingress controller to be explicitly utilised instead of "gce"
      # This is required to allow nginx-ingress-controller to function. This will override any cloud provided ingress controllers and use the one we choose to deploy, i.e. nginx.
      kubernetes.io/ingress.class: nginx
    hosts:
      - binder.hub23.turing.ac.uk
    tls:
      - secretName: hub23-binder-tls
        hosts:
          - binder.hub23.turing.ac.uk

  jupyterhub:
    ingress:
      enabled: true
      annotations:
        kubernetes.io/tls-acme: "true"
        kubernetes.io/ingress.class: nginx
      hosts:
        - hub.hub23.turing.ac.uk
      tls:
        - secretName: hub23-hub-tls
          hosts:
            - hub.hub23.turing.ac.uk
```

#### 8. Switch Binder and JupyterHub to use ClusterIPs in `values.yaml`

```yaml
binderhub:
  service:
    type: ClusterIP
  jupyterhub:
    proxy:
      service:
        type: ClusterIP
```

#### 9. Perform helm upgrade again

```bash
cd hub23-chart && helm dependency update && cd ..
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml \
    --force
```

**NOTE:** We use the `--force` flag here to avoid a `nodePorts` error.

#### 10. Updating the A records

By running the following command, we will see that the external IPs of Binder and JupyterHub have disappeared and we instead have one from the `nginx-ingress` load balancer.

```bash
kubectl get svc -n hub23
```

In the [Azure Portal](https://portal.azure.com), we will need to change our A records for the subdomain to both point to this new IP address.
Instructions on how to set A records are in [docs/08-enabling-page-redirection.md](08-enabling-page-redirection.md).

It is also recommended (though not necessary) to change the TTL (time to live) to 5 minutes (if not already set) as this will speed up propagation.

#### 11. Perform another helm upgrade

We upgrade the cluster to check the dummy certificates from "staging" works.

```bash
cd hub23-chart && helm dependency update && cd ..
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml \
```

You can watch the `cert-manager` pods make the request by running the following command:

```bash
kubectl get pods -n hub23 --watch
```

Use `^C` ("control and C") to exit.

#### 12. Switch to the "production" cluster issuer

Once the dummy certificates have been verfied, we can now switch over to the production cluster issuer which will actually enable HTTPS.
Add the following to `deploy/prod.yaml`:

```yaml
cert-manager:
  ingressShim:
    defaultIssuerName: "prod"
```

This overwrites the "staging" issuer set in `hub23-chart/values.yaml`.

#### 13. Perform the last helm upgrade

One last helm upgrade should complete the process.

```bash
cd hub23-chart && helm dependency update && cd ..
helm upgrade hub23 ./hub23-chart \
    -f deploy/prod.yaml \
    -f .secret/prod.yaml \
```

It may take some time for all the Named Servers hosting your subdomain to update to HTTPS.
Checking in an incognito browser may also help.
