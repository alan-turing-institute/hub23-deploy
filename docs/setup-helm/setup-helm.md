(content:helm:setup)=
# Setting up Helm

Helm is a package manager for Kubernetes and is used for installing, managing and upgrading applications on the cluster.
Helm is used to deploy apps using Charts.
Charts are a collection of information on how to install software and acts as a templating engine.
A Helm Chart will populate various configuration files with the required info and wraps the `kubectl apply` command to install/upgrade the package.

## Verify the installation

To verify the installation, run the following command.

```bash
helm list
```

You should see an empty list since no Helm charts have been installed:

```bash
NAME    NAMESPACE       REVISION        UPDATED STATUS  CHART   APP VERSION
```
