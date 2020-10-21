(content:cert-manager:deploy)=
# Deploying `cert-manager`

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
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v1.0.3/cert-manager.crds.yaml
```

## Install using Helm

```bash
helm install cert-manager jetstack/cert-manager \
    --version v1.0.3 \
    --namespace cert-manager \
    -f deploy/cert-manager.yaml
```
