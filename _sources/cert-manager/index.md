(content:cert-manager)=
# Enabling HTTPS using `cert-manager`

This document will walk through the steps required to enable HTTPS for deployments in your Kubernetes cluster using [`cert-manager`](https://docs.cert-manager.io/en/latest/).

Some of the following documentation is based on [this WIP documentation](https://discourse.jupyter.org/t/wip-documentation-about-cert-manager/2068).

```{warning}
Since Hub23 shares infrastructure with the turing.mybinder.org, parts of these docs should **not** be executed.
The `cert-manager` deployment itself should be managed from the [mybinder.org-deploy repo](https://github.com/jupyterhub/mybinder.org-deploy)
```

## Table of Contents

- {ref}`content:cert-manager:install`
- {ref}`content:cert-manager:context`
- {ref}`content:cert-manager:create-files`
- {ref}`content:cert-manager:deploy`
- {ref}`content:cert-manager:refs`
