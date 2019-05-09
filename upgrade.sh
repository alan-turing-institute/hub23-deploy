#!/bin/bash

helm repo update
helm upgrade hub23 jupyterhub/binderhub --version=$1 -f .secret/secret.yaml -f .secret/config.yaml
