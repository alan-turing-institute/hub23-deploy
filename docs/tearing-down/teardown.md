(content:teardown:teardown)=
# Tearing down your Deployment

Tearing down your JupyterHub entails:

1. Deleting your Kubernetes namespace, which deletes all objects created and managed by Kubernetes in it.
2. Deleting any cloud resources you’ve requested from the cloud provider.
3. Running a final check to make sure there aren’t any lingering resources that haven’t been deleted (e.g., storage volumes in some cloud providers).

```{warning}
Since Hub23 now shares the same Kubernetes infrastructure as the Turing Federation BinderHub, these docs are only here for clarity and should not be acted upon without first notifying the mybinder.org operating team and removing the Turing's BinderHub from the Federation.
```

## Delete the Helm Release and Kubernetes Namespace

First, delete the Helm release.
This deletes all resources that were created by Helm for Hub23.

```bash
helm delete hub23
```

Second, delete the Kubernetes namespace the hub was installed in.
This deletes any disks that may have been created to store user’s data, and any IP addresses that may have been provisioned.

```bash
kubectl delete namespace hub23
```

## Delete the Azure Resource Group

The next step is to delete all the resources created and that can be done in one command by deleting the resource group.

```bash
az group delete --name hub23
```

## Check the resources have truly been deleted!

Once the above command has completed, it is best practice to examine your Azure subscription in the Portal to ensure all resources have been deleted.
You will still be charged for any that remain.
