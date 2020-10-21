# Deploy the Kubernetes cluster

## Create the AKS cluster

The following command will deploy a Kubernetes cluster into the Hub23 resource group.
This command has been known to take between 7 and 30 minutes to execute depending on resource availability in the location we set when creating the resource group.

```bash
az aks create \
    --name hub23cluster \
    --resource-group Hub23 \
    --kubernetes-version 1.16.15 \
    --ssh-key-value .secret/ssh-key-hub23cluster.pub \
    --node-count 3
    --node-vm-size Standard_D2s_v3 \
    --service-principal $(cat .secret/appID.txt) \
    --client-secret $(cat .secret/key.txt) \
    --dns-service-ip 10.0.0.10 \
    --docker-bridge-address 172.17.0.1/16 \
    --network-plugin azure \
    --network-policy azure \
    --service-cidr 10.0.0.0/16 \
    --vnet-subnet-id $SUBNET_ID \
    --output table
```

- `--kubernetes-version`: It's recommended to use the most up-to-date version of Kubernetes.
- `--node-count` is the number of nodes to be deployed. 3 is recommended for a stable, scalable cluster.
- `--node-vm-size` denotes the type of virtual machine to be deployed. A list of Linux types can be found [here](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/).
- `--dns-service-ip`: An IP address assigned to the Kubernetes DNS service.
- `--docker-bridge-address`: A specific IP address and netmask for the Docker bridge, using standard CIDR notation.
- `--network-plugin`: The Kubernetes network plugin to use.
- `--network-policy`: The Kubernetes network policy to use.
- `--service-cidr`: A CIDR notation IP range from which to assign service cluster IPs.
- `--vnet-subnet-id`: The ID of a subnet in an existing VNet into which to deploy the cluster.

### Enable Autoscaling

To enable autoscaling on the cluster, add the following flags to the above `az aks create` command.

```bash
--enable-cluster-autoscaler
--min-count MINIMUM_NUMBER_OF_NODES
--max-count MAXIMUM_NUMBER_OF_NODES
```

- `--enable-cluster-autoscaler` enables the Kubernetes autoscaler
- `--min-count`/`--max-count` defines the minimum and maximum number of nodes to be spun up/down

### Create multiple nodepools

To create multiple nodepools within your Kubernetes cluster, add the following flags to the above `az aks create` command.

```bash
--nodepool-name { core | user }
--nodepool-labels hub.jupyter.org/node-purpose={ core | user }
```

- `--nodepool-name` assigns a name to your new nodepool
- `--nodepool-labels` allows the definition of labels that will propagate to all nodes within the nodepool

It is recommended to use iether `core` or `user` to name/label these nodepools as BinderHub will try to schedule pods according to these labels.

```{warning}
The first nodepool create (i.e. with `az aks create` command) cannot be deleted as it contains the `kubeadmin` kubelet.
```

Another nodepool can then be added as follows:

```bash
az aks nodepool add \
    --cluster-name hub23cluster \
    --name user \
    --resource-group Hub23 \
    --kubernetes-version 1.16.15 \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --vnet-subnet-id $SUBNET_ID \
    --labels hub.jupyter.org/node-purpose=user \
    --output table
```

```{note}
See the [`az aks nodepool` docs](https://docs.microsoft.com/en-us/cli/azure/aks/nodepool?view=azure-cli-latest) for more info and commands.
```

```{note}
The flags to enable autoscaling can also be used here.
```

### Delete local copies of the secret files

Once the Kubernetes cluster is deployed, you should delete the local copy of the Service Principal and public SSH key.

```bash
rm .secret/ssh-key-hub23cluster.pub
rm .secret/appID.txt
rm .secret/key.txt
```

## Get credentials for `kubectl`

We need to configure the local installation of the Kubernetes CLI to work with the version deployed onto the cluster, and do so with the following command.

```bash
az aks get-credentials \
    --name hub23cluster \
    --resource-group Hub23 \
    --output table
```

This command would need to be repeated when trying to manage the cluster from another computer or if you have been working with a different cluster.

## Check the cluster is fully functional

Output the status of the nodes.

```bash
kubectl get nodes
```

All nodes should have `STATUS` as `Ready`.
