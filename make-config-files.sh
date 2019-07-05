#!/bin/bash

# Script to automatically populate secret-template.yaml and
# config-template.yaml with values and secrets in order to
# connect to the Turing BinderHub (Hub23)

# Variables
sub=Turing-BinderHub         # Azure BinderHub subscription
res_grp=Hub23                # Azure Resource Group
vault_name=hub23-keyvault    # Key vault name
cluster=hub23cluster         # k8s cluster name
registry=hub23registry       # Azure Container Registry
prefix=hub23/binder-dev      # Docker image prefix
org_name=binderhub-test-org  # GitHub organisation name
hub_name=hub23               # BinderHub name

secret_names=(
  apiToken
  secretToken
  binderhub-access-token
  github-client-id
  github-client-secret
  SP-appID
  SP-key
)

# Login to Azure
az login -o none

# Set subscription
az account set -s ${sub}

# Configure Azure credentials for hub23cluster
az aks get-credentials -n ${cluster} -g ${res_grp}

# Initialise helm
helm init --client-only

# Make sure the JupyterHub/BinderHub Helm Chart repo is installed and up-to-date
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update

# get IP addresses of JupyterHub and Binder
jupyter_ip=`kubectl get svc proxy-public -n ${hub_name} | awk '{ print $4}' | tail -n 1`
binder_ip=`kubectl get svc binder -n ${hub_name} | awk '{ print $4}' | tail -n 1`

# Make a secrets folder
mkdir -p .secret

# Download secrets
for secret_name in ${secret_names[@]}; do
  az keyvault secret download \
  --vault-name ${vault_name} \
  -n ${secret_name} \
  -f .secret/${secret_name}.txt
done

# Populate .secret/secret.yaml
sed -e "s/<apiToken>/$(cat .secret/apiToken.txt)/" \
  -e "s/<secretToken>/$(cat .secret/secretToken.txt)/" \
  -e "s/<acr-name>/${registry}/" \
  -e "s/<username>/$(cat .secret/SP-appID.txt)/" \
  -e "s/<password>/$(cat .secret/SP-key.txt)/" \
  -e "s/<accessToken>/$(cat .secret/binderhub-access-token.txt)/" \
  secret-template.yaml > .secret/secret.yaml

# Populate .secret/config.yaml
sed -e "s/<acr-name>/${registry}/g" \
  -e "s@<prefix>@${prefix}@" \
  -e "s/<jupyter-ip>/${jupyter_ip}/" \
  -e "s/<binder-ip>/${binder_ip}/" \
  -e "s/<github-oauth-id>/$(cat .secret/github-client-id.txt)/" \
  -e "s/<github-oauth-secret>/$(cat .secret/github-client-secret.txt)/" \
  -e "s/<github-org-name>/${org_name}/" \
  config-template.yaml > .secret/config.yaml

# Delete downloaded secret files
for secret_name in ${secret_names[@]}; do
  rm .secret/${secret_name}.txt
done

# End the script with some outputs
echo
echo Your BinderHub files have been configured:
echo ".secret/config.yaml        .secret/secret.yaml"
echo
echo "Binder IP: " `kubectl get svc binder -n ${hub_name} | awk '{ print $4}' | tail -n 1`
