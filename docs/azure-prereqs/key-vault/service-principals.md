# Service Principal

When deploying a Kubernetes cluster onto Azure, a Service Principal is required.
A Service Principal is a protocol, consisting of an app ID and a key, that grants the cluster permissions to act on behalf of both the user and itself.
REG members presently don't have permissions to create Service Principals and so IT Services create them on our behalf via a TopDesk request.
I ([**@sgibson91**](https://github.com/sgibson91)) have saved the Service Principal to the key vault for safe-keeping.
The following steps document how I did it and how one would download the Service Principal again.

Add the app ID:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name SP-appID \
    --value <redacted>
```

Add the key:

```bash
az keyvault secret set \
    --vault-name hub23-keyvault \
    --name SP-key \
    --value <redacted>
```

Download the app ID and save to a file:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-appID \
    --file .secret/appID.txt
```

Download the key and save to a file:

```bash
az keyvault secret download \
    --vault-name hub23-keyvault \
    --name SP-secret \
    --file .secret/key.txt
```
