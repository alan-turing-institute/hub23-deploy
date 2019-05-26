# Billing

This folder contains Azure billing information for Cloud resources in
[`hub23_billing.yaml`](hub23_billing.yaml) and a script to calculate the amount
of Azure credits (in $USD) that should be requested to continue running the Hub23
BinderHub for a year, with a given contingency for autoscaling.

You should check that the information in [`hub23_billing.yaml`](hub23_billing.yaml)
is still up to date.
VM pricing is [here](https://azure.microsoft.com/en-gb/pricing/details/virtual-machines/linux/)
and Container Registry pricing is [here](https://azure.microsoft.com/en-gb/pricing/details/container-registry/).
Make sure to select the "West Europe" location and we list the prices in $USD.

To calculate how much credit you should request via the TopDesk ticketing system,
run the [Python script](calculate_billing.py) in this directory.

This script requires Python version >= 3.6.

```
cd billing
pip install -r requirements.txt
python calculate_billing.py
```

This will output the total yearly cost of the ACR and Kubernetes cluster with and
without a contingency. By default, the script calculates a 10% contingency but other
contingencies may be calculated by parsing the `--contingency` flag.

```
python calculate_billing.py --contingency 20
```
where `20` is 20% (not 0.2!).

A breakdown of costs will be output as `hub23_billing_calc.yaml`.
