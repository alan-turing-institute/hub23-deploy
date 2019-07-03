#!/usr/bin/env bash

# Print pods
echo "--> Printing pods"
kubectl get pods -n ${1}
echo

# Get IP addresses of both the JupyterHub and BinderHub
echo "JupyterHub IP: " `kubectl --namespace=${1} get svc proxy-public | awk '{ print $4}' | tail -n 1`
echo "Binder IP: " `kubectl --namespace=${1} get svc binder | awk '{ print $4}' | tail -n 1`
