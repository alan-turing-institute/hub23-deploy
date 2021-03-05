(content:k8s:upgrade)=
# Upgrading the Kubernetes cluster

It is recommended to keep the version of Kubernetes on the cluster up-to-date with a recent stable version.
Follow the steps in {ref}`content:k8s:version` to find such a version.

## Master upgrade

To upgrade the master version of the cluster, run the following:

```bash
az aks upgrade --name hub23cluster --resource-group hub23 --kubernetes-version VERSION --output table
```

## Nodepool upgrade

Then to upgrade each nodepool in the cluster, run the following:

```bash
az aks nodepool upgrade --resource-group hub23 --cluster-name hub23cluster --name NODEPOOL_NAME --kubernetes-version VERSION --output table
```
