#!/bin/bash

# Script to automatically populate secret-template.yaml and
# config-template.yaml with values and secrets in order to
# connect to the Turing BinderHub (Hub23)

# Variables
sub=Turing-BinderHub       # Azure BinderHub subscription
res_grp=Hub23              # Azure Resource Group
vault_name=hub23-keyvault  # Key vault name
cluster=hub23cluster       # k8s cluster name
docker_org=binderhubtest   # DockerHub organisation
prefix=hub23-dev           # Docker image prefix
jupyter_ip=104.40.238.90   # IP address of JupyterHub
binder_ip=52.232.80.19     # IP address of Binder page

# Get DockerHub login details
# User MUST be a member of docker_org
echo Please provide your DockerHub login details.
echo This DockerHub account MUST be a member of: ${docker_org}
read -p "DockerHub ID: " docker_id
read -sp "DockerHub password: " docker_pass
echo

# Login to Azure
az login --output none

# Set subscription
az account set -s ${sub}

# Configure Azure credentials for hub23cluster
az aks get-credentials --name ${cluster} --resource-group ${res_grp} --output table

# Initialise helm
helm init --client-only

# Make sure the JupyterHub/BinderHub Helm Chart repo is installed and up-to-date
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update

# Make a secrets folder
mkdir -p .secret

# Download apiToken
az keyvault secret download --vault-name ${vault_name} -n apiToken -f .secret/apiToken.txt

# Download secretToken
az keyvault secret download --vault-name ${vault_name} -n secretToken -f .secret/secretToken.txt

# Download GitHub client ID
#az keyvault secret download --vault-name ${vault_name} -n clientId -f .secret/clientId.txt

# Download GitHub client secret
#az keyvault secret download --vault-name ${vault_name} -n clientSecret -f .secret/clientSecret.txt

# Populate .secret/secret.yaml
sed -e "s/<apiToken>/$(cat .secret/apiToken.txt)/" \
  -e "s/<secretToken>/$(cat .secret/secretToken.txt)/" \
  -e "s/<docker-id>/$docker_id/" \
  -e "s/<password>/$docker_pass/" secret-template.yaml > .secret/secret.yaml

# Populate .secret/config.yaml
sed -e "s/<docker-org>/${docker_org}/" \
  -e "s/<prefix>/${prefix}/" \
  -e "s/<jupyter-ip>/${jupyter_ip}/" \
  -e "s/<binder-ip>/${binder_ip}/" \
#  -e "s/<clientId>/$(cat .secret/clientId.txt)/" \
#  -e "s/<clientSecret>/$(cat .secret/clientSecret.txt)/" \
  config-template.yaml > .secret/config.yaml

# Delete downloaded secret files
rm .secret/apiToken.txt
rm .secret/secretToken.txt
#rm .secret/clientId.txt
#rm .secret/clientSecret.txt

# End the script with some outputs
echo Your BinderHub files have been configured:
echo ".secret/config.yaml        .secret/secret.yaml"
echo
echo "Binder IP: " `kubectl --namespace=hub23 get svc binder | awk '{ print $4}' | tail -n 1`
