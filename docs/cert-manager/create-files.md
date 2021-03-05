(content:cert-manager:create-files)=
# Creating files

Some extra files are required which we will outline below.

The resulting file structure will look as follows:

```bash
|-deploy/
| |-letsencrypt-staging.yaml
| |-letsencrypt-prod.yaml
|
|-hub23-chart/
| |-files/
| |-templates/
| | |-issuer.yaml
| | |-user-configmap.yaml
| |-Chart.yaml
| |-requirements.yaml
| |-values.yaml
```

We will have already created `Chart.yaml`, `requirements.yaml` and `values.yaml` in {ref}`content:binderhub:local-chart`.

## Create `templates/issuer.yaml`

```yaml
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: hub23-letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: hub23registry@turing.ac.uk
    privateKeySecretRef:
      name: hub23-letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: hub23-letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: hub23registry@turing.ac.uk
    privateKeySecretRef:
      name: hub23-letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

## Create `deploy/letsencrypt-staging.yaml` and `deploy/letsencrypt-prod.yaml`

### `deploy/letsencrypt-staging.yaml`

```yaml
binderhub:
  ingress:
    annotations:
      cert-manager.io/issuer: "hub23-letsencrypt-staging"

  jupyterhub:
    ingress:
      annotations:
        cert-manager.io/issuer: "hub23-letsencrypt-staging"
```

### `deploy/letsencrypt-prod.yaml`

```yaml
binderhub:
  ingress:
    annotations:
      cert-manager.io/issuer: "hub23-letsencrypt-prod"

  jupyterhub:
    ingress:
      annotations:
        cert-manager.io/issuer: "hub23-letsencrypt-prod"
```
