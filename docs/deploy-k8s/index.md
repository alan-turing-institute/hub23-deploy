(content:k8s)=
# Deploy a Kubernetes Cluster with AKS

This section covers deploying a Kubernetes cluster with Azure Kubernetes Service (AKS).
It includes instructions for a standard cluster, or one with autoscaling or multiple nodepools enabled.
These instructions can be combined to create a cluster with **both** autoscaling and multiple nodepools.

```{warning}
Since Hub23 now shares the same Kubernetes infrastructure as the Turing Federation BinderHub, the following docs are only here for clarity and should not be acted upon without first notifying the mybinder.org operating team and removing the Turing's BinderHub from the Federation.
```

## Table of Contents

- {ref}`content:k8s:install`
- {ref}`content:k8s:download-secrets`
- {ref}`content:k8s:net-pols`
- {ref}`content:k8s:create`
- {ref}`content:k8s:upgrade`
- {ref}`content:k8s:refs`
