# Customising the JupyterHub

Certain customisations can be made to the JupyterHub supporting Hub23 to provide a more tailored user experience.

See the following docs:
* https://zero-to-jupyterhub.readthedocs.io/en/latest/reference.html
* https://zero-to-jupyterhub.readthedocs.io/en/latest/user-resources.html
* https://zero-to-jupyterhub.readthedocs.io/en/latest/user-environment.html

## Customising User Resources

The most import customisation to the JupyterHub will be the compute resources each user pod has access to.
This affects what kind of computations can be run in an active Binder instance and the overall cost of running the BinderHub.

We can _guarantee_ each user pod a certain amount of resources and _limit_ them to another value (that is, they could use slightly more than allocated if need be).

We can set the CPU and RAM memory guarantees and limits with the following code snippet in `.secret/config.yaml`.

```
# EXAMPLE VALUES
jupyterhub:
  singleuser:
    memory:
      limit: 1G
      guarantee: 1G
    cpu:
      limit: .5
      guarantee: .5
```
