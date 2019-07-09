#!/bin/bash

# Initialise helm
helm init --client-only

# Make sure the JupyterHub/BinderHub Helm Chart repo is installed and up-to-date
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update
# Update local chart
cd Hub23 && helm dependency update && cd ..

helm upgrade --wait --install hub23 Hub23 --version=v0.0.1 -f deploy/prod.yaml -f .secret/prod.yaml
echo
kubectl get pods -n hub23
echo
echo "Binder IP (binder.hub23.turing.ac.uk): " `kubectl get svc binder -n hub23 | awk '{ print $4}' | tail -n 1`
