# Creating files

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

## Create `templates/cluster-issuer.yaml`

```yaml
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

## Create `deploy/cert-manager.yaml`

```yaml
ingressShim:
  defaultIssuerName: letsencrypt-prod
  defaultIssuerKind: ClusterIssuer
```
