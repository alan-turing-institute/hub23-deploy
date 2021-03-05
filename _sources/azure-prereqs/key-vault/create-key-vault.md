(content:key-vault:create)=
# Create the Key Vault

## Create the key vault

```{note}
Key vault names must be lower case and/or numerical and may only include hyphens (`-`), no underscores (`_`) or other non-alphanumeric characters. They must also be unique.
```

```bash
az keyvault create --name hub23-keyvault --resource-group hub23
```
