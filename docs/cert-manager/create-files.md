(content:cert-manager:create-files)=
# Creating files

Some extra files are required which we will outline below.

The resulting file structure will look as follows:

```bash
hub23-chart/
|-files/
|-templates/
| |-issuer.yaml
| |-user-configmap.yaml
|
|-Chart.yaml
|-requirements.yaml
|-values.yaml
```

We will have already created `Chart.yaml`, `requirements.yaml` and `values.yaml` in {ref}`content:binderhub:local-chart`.

## Create `templates/issuer.yaml`

```yaml
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
