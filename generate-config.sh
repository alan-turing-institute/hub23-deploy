#!/bin/bash

# Script to automatically populate secret-template.yaml and
# config-template.yaml with values and secrets in order to
# connect to the Turing BinderHub (Hub23)

# Variables
res_grp=Hub23                         # Azure Resource Group
vault_name=hub23-keyvault             # Key vault name
cluster=hub23cluster                  # k8s cluster name
registry=hub23registry                # Azure Container Registry
prefix=hub23/binder-dev               # Docker image prefix
org_name=binderhub-test-org           # GitHub organisation name
hub_name=hub23                        # BinderHub name
jupyterhub_ip=hub.hub23.turing.ac.uk  # JupyterHub address
binder_ip=binder.hub23.turing.ac.uk   # Binder page address

secret_names=(
  apiToken
  secretToken
  binderhub-access-token
  github-client-id
  github-client-secret
  SP-appID
  SP-key
)

# Authenticate to k8s cluster
az aks get-credentials -n ${cluster} -g ${res_grp}

# Make a secrets folder
mkdir -p .secret

# Download secrets
for secret_name in ${secret_names[@]}; do
  az keyvault secret download \
  --vault-name ${vault_name} \
  -n ${secret_name} \
  -f .secret/${secret_name}.txt
done

# Populate .secret/prod.yaml
sed -e "s/<acr-name>/${registry}/g" \
  -e "s/<apiToken>/$(cat .secret/apiToken.txt)/" \
  -e "s/<secretToken>/$(cat .secret/secretToken.txt)/" \
  -e "s/<username>/$(cat .secret/SP-appID.txt)/" \
  -e "s/<password>/$(cat .secret/SP-key.txt)/" \
  prod-template.yaml > .secret/prod.yaml

# Delete downloaded secret files
for secret_name in ${secret_names[@]}; do
  rm .secret/${secret_name}.txt
done

# End the script with some outputs
echo
echo Your BinderHub files have been configured:
ls .secret/
echo
echo "Binder IP (binder.hub23.turing.ac.uk): " `kubectl get svc binder -n ${hub_name} | awk '{ print $4}' | tail -n 1`
