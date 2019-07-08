#!/usr/bin/env bash

# Print pods
echo "--> Printing pods"
kubectl get pods -n hub23
echo

# Get IP addresses of both the JupyterHub and BinderHub
echo "--> Printing IP addresses"
echo "JupyterHub IP (hub.hub23.turing.ac.uk): " `kubectl --namespace=hub23 get svc proxy-public | awk '{ print $4}' | tail -n 1`
echo "Binder IP (binder.hub23.turing.ac.uk): " `kubectl --namespace=hub23 get svc binder | awk '{ print $4}' | tail -n 1`
