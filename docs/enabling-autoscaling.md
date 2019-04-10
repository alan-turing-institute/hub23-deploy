# Optimizing the JupyterHub for Auto-Scaling

See the following docs:
* https://zero-to-jupyterhub.readthedocs.io/en/latest/optimization.html
* https://discourse.jupyter.org/t/planning-placeholders-with-jupyterhub-helm-chart-0-8-tested-on-mybinder-org/213/6
* https://zero-to-jupyterhub.readthedocs.io/en/latest/reference.html

## Efficient Cluster Autoscaling

A [Cluster Autoscaler (CA)](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler) will help add and remove nodes from the cluster.
It needs to scale up before users arrive and scale down nodes aggressively enough without disrupting users.

### Scaling up in time (user placeholders)

A CA will add nodes when pods don't fit on the available nodes but would fit if another node is added.
But this can lead to a long waiting time for the user as a pod is spun up.

Kubernetes 1.11+ (and Helm 2.11+) introduced [Pod Priority and Preemption](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/).
Pods with higher priority can preempt/evict pods with lower priority if that would help the higher priority pod fit on a node.

Hence dummy users or _user-placeholders_ with low priority can be added to take up resources until a real user (with higher priority) requires it.
The lower priority pod will be preempted to make room for the higher priority pod.
The now evicted user-placeholder will signal the CA that it needs to scale up.

User placeholders will have the same resource requests as the default user.
Therefore, if you have 3 user placeholders running, real users will only need to wait for a scale up if more than 3 users arrive in a time interval less than it takes to make a node ready for use.

## Installing a Cluster Autoscaler on an existing AKS cluster

See the following docs:
* https://docs.microsoft.com/en-us/azure/aks/cluster-autoscaler

#### 1. Install aks-preview CLI extension

```
az extension add --name aks-preview
```

#### 2. Register scale set feature provider

```
az feature --name VMSSPreview --namespace Microsoft.ContainerServie
```

This will take a while to register.
Run the following command to check the status.

```
az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/VMSSPreview')].{Name:name,State:properties.state}"
```

#### 3. Refresh the registration

```
az provider register --namespace Microsoft.ContainerService
```

#### 4. Update Kubernetes version on AKS cluster

The cluster autoscaler reguires Kubernetes version >= 1.12.4.

Run the following command to see available upgrades.

```
az aks get-upgrades --resource-group Hub23 --name hub23cluster --output table
```

Update the cluster to v1.12.7.

```
az aks upgrade --resource-group Hub23 --name hub23cluster --kubernetes-version 1.12.7
```

This will take a while to execute and the cluster will not be available during the upgrade.




## Pre-Pulling images

A user will have to wait for a requested Docker image if it isn't already pulled onto that node.
If the image is large, this can be a long wait!

In the case when a new node is added (Cluster Autoscaler), the _continuous-image-puller_ will pull a user's container.
This users a daemonset to force Kubernetes to pull the user image on all nodes as soon as a node is present.

The continuous-image-puller is disabled by default and the following snippet is added to `config.yaml` to enable it.

```
config:
  jupyterhub:
    hub:
      prePuller:
        continuous:
          # NOTE: if used with a Cluster Autoscaler, also add user-placeholders
          enabled: true
```
