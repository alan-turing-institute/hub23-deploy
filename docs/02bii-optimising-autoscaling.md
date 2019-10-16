# Optimizing the JupyterHub for Autoscaling

See the following docs:

- <https://zero-to-jupyterhub.readthedocs.io/en/latest/user-management.html#culling-user-pods>
- <https://zero-to-jupyterhub.readthedocs.io/en/latest/optimization.html>
- <https://discourse.jupyter.org/t/planning-placeholders-with-jupyterhub-helm-chart-0-8-tested-on-mybinder-org/213>
- <https://zero-to-jupyterhub.readthedocs.io/en/latest/reference.html>

All config code snippets should be added to `deploy/config.yaml`.

Table of Contents:

- [Culling user pods](#culling-user-pods)
- [Efficient Cluster Autoscaling](#efficient-cluster-autoscaling)
  - [Scaling up in time (user placeholders)](#scaling-up-in-time-user-placeholders)
  - [Scaling down efficiently](#scaling-down-efficiently)
    - [Labelling nodes for core purpose](#labelling-nodes-for-core-purpose)
- [Using available nodes efficiently (user scheduler)](#using-available-nodes-efficiently-user-scheduler)
- [Pre-Pulling images](#pre-pulling-images)

---

## Culling user pods

JupyterHub will automatically delete any user pods that have no activity for a period of time.
This helps free up computational resources and keeps costs down if you are using an autoscaling cluster.

In JupyterHub, “inactivity” is defined as no response from the user’s browser.
JupyterHub constantly pings the user’s JupyterHub browser session to check whether it is open.
This means that leaving the computer running with the JupyterHub window open will **not** be treated as inactivity.

By default, JupyterHub will run the culling process every ten minutes and will cull any user pods that have been inactive for more than one hour.
You can configure this behavior in your `config.yaml` file with the following code snippet.
The culler can also be configured to cull pods that have existed for over a given length of time via the `maxAge` argument.

```yaml
cull:
  timeout: <max-idle-seconds-before-user-pod-is-deleted>
  every: <number-of-seconds-this-check-is-done>
  maxAge: <number-of-seconds-the-pods-has-been-active>
```

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

User-placeholders will have the same resource requests as the default user.
Therefore, if you have 3 user placeholders running, real users will only need to wait for a scale up if more than 3 users arrive in a time interval less than it takes to make a node ready for use.

Add the following code snippet to use 3 user-placeholders.

```yaml
config:
  jupyterhub:
  scheduling:
    podPriority:
      enabled: true
    userPlaceholder:
      # Specify three dummy user pods will be used as placeholders
      replicas: 3
```

### Scaling down efficiently

To scale down, [certain technical criteria](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md#what-types-of-pods-can-prevent-ca-from-removing-a-node) need to be met.
Most importantly for a node to be scaled down, it must be free from pods that are not allowed to be disrupted.
Such pods are for example real user pods, important system pods, and some JupyterHub pods.

Consider the following scenario.
Many users arrive to the JupyterHub during the day causing new nodes to be added by the CA.
Some system pods end up on the new nodes with user pods.
At night, when the _culler_ has removed many inactive pods, the nodes are now free from user pods but cannot be removing since there is a single system pod remaining.

We setup a node affinity for core pods to remain on the 3 nodes that were deployed.
See [docs/02bi-deploy-binderhub-with-autoscaling.md](02bi-deploy-binderhub-with-autoscaling.md)

#### Labelling nodes for core purpose

Add a `core` label to all the nodes in the node pool.

1. Setup a node pool (with autoscaling; `docs/deploy-binderhub-with-autoscaling.md`) and a certain label.

   1. The label: `hub.jupyter.org/node-purpose=core`

      ```bash
      kubectl label nodes <node-name> hub.jupyter.org/node-purpose=core
      ```

      Use `kubectl get nodes` to ascertain `<node-name>`.

2. Make core pods require to be scheduled on the node pool setup above.

   The default setting is to make core pods _prefer_ to be scheduled on nodes with the `hub.jupyter.org/node-purpose=core` label, but we can make it a _requirement_ by using the code snippet below.

   ```yaml
   config:
     jupyterhub:
       scheduling:
         corePods:
           nodeAffinity:
             # matchNodePurpose valid options:
             # - ignore
             # - prefer (the default)
             # - require
             matchNodePurpose: require
   ```

This process can be repeated for a `user` label.

## Using available nodes efficiently (user scheduler)

If you have users starting new servers while the total number of active users is decreasing, how will you free up a node so it can be scaled down?

This is what the _user scheduler_ is for.
It's only task is to schedule new user pods to the _most utilised node_.
This can be compared to the _default scheduler_ that instead always tries to schedule pods so the _least utilised node_.
Only the user scheduler would allow the underutilised nodes to free up over time as the total amount of users decrease but a few users still arrive.

**NOTE:** IF you don't want to scale down, it makes more sense to let users spread out and utilise all available nodes.
Only activate the user scheduler if you have an autoscaling node pool.

Enable the user scheduler with the following code snippet:

```yaml
config:
  jupyterhub:
    scheduling:
      userScheduler:
        enabled: true
```

## Pre-Pulling images

A user will have to wait for a requested Docker image if it isn't already pulled onto that node.
If the image is large, this can be a long wait!

In the case when a new node is added (Cluster Autoscaler), the _continuous-image-puller_ will pull a user's container.
This uses a daemonset to force Kubernetes to pull the user image on all nodes as soon as a node is present.

The continuous-image-puller is disabled by default and the following snippet is added to `config.yaml` to enable it.

```yaml
config:
  jupyterhub:
    hub:
      prePuller:
        continuous:
          # NOTE: if used with a Cluster Autoscaler, also add user-placeholders
          enabled: true
```
