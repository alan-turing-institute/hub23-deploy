(content:cert-manager:deploy)=
# Deploying `cert-manager`

```{warning}
Since Hub23 shares infrastructure with the turing.mybinder.org, this step should **not** be executed.
Instead the `cert-manager` deployment should be managed from the [mybinder.org-deploy repo](https://github.com/jupyterhub/mybinder.org-deploy)
```

## Create a namespace for `cert-manager`

```bash
kubectl create namespace cert-manager
```

## Add the `cert-manager` chart repo to Helm

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

## Install the Custom Resource Definitions

```bash
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v{INSERT_VERSION_NUMBER_HERE}/cert-manager.crds.yaml
```

## Install using Helm

```bash
helm install cert-manager jetstack/cert-manager \
    --version VERSION \
    --create-namespace \
    --namespace cert-manager \
    --timeout 5m0s \
    --wait
```
