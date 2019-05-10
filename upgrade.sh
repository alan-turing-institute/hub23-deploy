#!/bin/bash

helm repo update
helm upgrade $1 jupyterhub/binderhub --version=$2 -f .secret/secret.yaml -f .secret/config.yaml
kubectl get pods -n $1
echo "Binder IP: " `kubectl get svc binder -n $1 | awk '{ print $4}' | tail -n 1`
