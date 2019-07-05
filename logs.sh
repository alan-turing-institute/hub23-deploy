#!/usr/bin/env bash

echo "--> Fetching JupyterHub logs"

# Get pod name of the JupyterHub
HUB_POD=`kubectl get pods -n hub23 -o=jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep "^hub-"`

# Print the JupyterHub logs to the terminal
kubectl logs ${HUB_POD} -n hub23
