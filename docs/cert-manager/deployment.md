(content:cert-manager:deploy)=
# Deploying `cert-manager`

## Deploying `cert-manager` into a namespace

```{warning}
Since Hub23 shares infrastructure with the turing.mybinder.org, this step should **not** be executed.
Instead the `cert-manager` deployment should be managed from the [mybinder.org-deploy repo](https://github.com/jupyterhub/mybinder.org-deploy)
```

### Create a namespace for `cert-manager`

```bash
kubectl create namespace cert-manager
```

### Add the `cert-manager` chart repo to Helm

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

### Install the Custom Resource Definitions

```bash
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v{INSERT_VERSION_NUMBER_HERE}/cert-manager.crds.yaml
```

### Install using Helm

```bash
helm install cert-manager jetstack/cert-manager \
    --version VERSION \
    --create-namespace \
    --namespace cert-manager \
    --timeout 5m0s \
    --wait
```

## Performing a `helm upgrade` with the `cert-manager` configs

When running `helm upgrade`, append either `-f deploy/letsencrypt-staging.yaml` or `-f deploy/letsencrypt-prod.yaml` to the command to enable the annotations in the cluster.
Using the `staging` config will allow you to test that `cert-manager` is installed and working correctly, whereas the `prod` config will actually request certificates for your domain.
