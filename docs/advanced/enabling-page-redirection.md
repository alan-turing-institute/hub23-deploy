# Enabling Page Redirection

These docs will walk through how to create a DNS at which the Binder page and JupyterHub are found.

## Creating a new DNS Zone

First we must create a DNS zone to handle the redirection of the pages.
We will create a subdomain in the Turing domain.

1. On the Azure Portal:
   - Click "+ Create a resource"
   - Search for "DNS zone"
   - Click "Create"
2. Set the subscription to "Turing-BinderHub" and select the "Hub23" resource group.
   (Or use a different/new subscription and resource group.)
   Set the **Name** field to the desired URL, in our case: `hub23.turing.ac.uk`.
   - If you created a new resource group, you will have to set its location.
3. Click "Review + create".
4. View the new DNS zone and copy the four nameservers in the "NS" record.
5. Send the nameserver to Turing IT Services.
   Ask them to add the subdomain's DNS record as an NS record for `hub23` in the `turing.ac.uk` DNS zone record.

## Creating A records

We will now set A records that point to the IP addresses of the JupyterHub and Binder page.

1. When viewing the DNS zone on the Azure Portal, click "+ Record set"
2. In the **Name** field, enter "binder" or "hub" (depending on which IP you choose to set a record for first, the process is the same for both).
3. Set **Alias record set** to "Yes" and this will bring up some new options.
4. Make sure the subscription is set to "Turing-BinderHub".
   Under **Azure resource** select one of the two items under **Public IP Address**.
   If you view these resources (under the resource group beginning `MC_`), you will be able to see the IP addresses they refer to. Compare these with the output of `kubectl get svc --namespace hub23` in order to ascertain which one is Binder and which is JupyterHub.
5. Click "OK" and repeat the process for the second IP address.

## Update `deploy/config.yaml`

Make sure to update `deploy/config.yaml` or `deploy/prod.yaml` to include the new DNS's, instead of the raw IP addresses.
If you have GitHub OAuth enabled, the DNS names will have to be inserted instead of the IP addresses in the OAuth app as well.
This shouldn't generate a new Client ID or Secret.
