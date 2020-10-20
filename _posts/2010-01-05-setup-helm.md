---
layout: page
share: false
title: "Setup Helm"
---

This documentation will walk through setting up Helm on the Kubernetes cluster.

We assume you have the following CLI installed:

- [Helm CLI](https://helm.sh/docs/using_helm/#installing-helm)

## Table of Contents

- [Setting up Helm](#setting-up-helm)

---

## Setting up Helm

Helm is a package manager for Kubernetes and is used for installing, managing and upgrading applications on the cluster.
Helm has two parts: a local client (`helm`) and a remote server (`tiller`).
When running `helm` commands in your local terminal, a message is relayed to `tiller` which executes the command across the remote cluster.
Helm is used to deploy apps using Charts.
Charts are a collection of information on how to install software and acts as a templating engine.
A Helm Chart will populate various configuration files with the required info and wraps the `kubectl apply` command to install/upgrade the package.

#### 1. Verify the installation

To verify the installation, run the following command.

```bash
helm list
```
