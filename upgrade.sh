#!/bin/bash

helm repo update
helm upgrade hub23 jupyterhub/binderhub --version=$1 -f .secret/secret.yaml -f .secret/config.yaml
echo
kubectl get pods -n hub23
echo
echo "Binder IP: " `kubectl get svc binder -n hub23 | awk '{ print $4}' | tail -n 1`
