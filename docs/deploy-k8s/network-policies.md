(content:k8s:net-pols)=
# Enable Network Policies

The BinderHub helm chart contains network policies designed to restrict access to pods and the JupyterHub.
However, the Kubernetes cluster will not be automatically configured to obey these network policies.
Therefore, we need create a virtual network (vnet) and sub network (subnet) with network policies enabled so that these pod traffic restrictions are obeyed.

## Create a VNET

```bash
az network vnet create \
    --resource-group Hub23 \
    --name hub23-vnet \
    --address-prefixes 10.0.0.0/8 \
    --subnet-name hub23-subnet \
    --subnet-prefix 10.240.0.0/16
```

- `--address-prefixes`: IP address prefixes for the VNet;
- `--subnet-prefix`: IP address prefixes in CIDR format for the new subnet.

## Retrieve the VNet ID

This saves the VNet ID into a bash variable.

```bash
VNET_ID=$(
    az network vnet show \
    --resource-group Hub23 \
    --name hub23-vnet \
    --query id \
    --output tsv
)
```

## Assign the Contributor role to the Service Principal for accessing the VNet

```bash
az role assignment create \
    --assignee $(cat .secret/appID.txt) \
    --scope $VNET_ID \
    --role Contributor
```

```{warning}
You must have Owner permissions on the subscription for this step to work.
```

## Retrieve the subnet ID

This will save the subnet ID to a bash variable.

```bash
SUBNET_ID=$(
    az network vnet subnet show \
    --resource-group Hub23 \
    --vnet-name hub23-vnet \
    --name hub23-subnet \
    --query id \
    --output tsv
)
```
