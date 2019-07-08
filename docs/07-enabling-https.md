# Enabling Page Redirection and HTTPS

These docs will walk through how to create a DNS at which the Binder page and JupyterHub are found and how to enable these addresses with HTTPS.

## Creating a new DNS Zone

First we must create a DNS zone to handle the redirection of the pages.
We will create a subdomain in the Turing domain.

1. On the Azure Portal:
   * Click "+ Create a resource"
   * Search for "DNS zone"
   * Click "Create"

2. Set the subscription to "Turing-BinderHub" and select the "Hub23" resource group.
   (Or use a different/new subscription and resource group.)
   Set the **Name** field to the desired URL, in our case: `hub23.turing.ac.uk`.
   * If you created a new resource group, you will have to set its location.

3. Click "Review + create".

4. View the new DNS zone and copy the four nameservers in the "NS" record.

5. Send the nameserver to Turing IT Services.
   Ask them to add the subdomain's DNS record as an NS record for `hub23` in the `turing.ac.uk` DNS zone record.

## Creating A records


