#!/usr/bin/env bash

# Print pods
echo "--> Printing pods"
kubectl get pods -n hub23
echo

# Get IP addresses of both the JupyterHub and BinderHub
echo "JupyterHub IP: " `kubectl --namespace=hub23 get svc proxy-public | awk '{ print $4}' | tail -n 1`
echo "Binder IP: " `kubectl --namespace=hub23 get svc binder | awk '{ print $4}' | tail -n 1`
