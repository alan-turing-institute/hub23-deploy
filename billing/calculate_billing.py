import yaml
import argparse


def parse_args():
    """
Parse command line arguments.

This function reads one command line argument which is the percentage
contingency desired when calculating costs for autoscaling of the cluster. If
not provided, this value defaults to 10%.
    """
    parser = argparse.ArgumentParser(
        description=("Parse a contingency percentage for calculating BinderHub "
                     "Cloud costs.")
    )

    parser.add_argument(
        "-c", "--contingency", default=10, type=int,
        help=("Parse the percentage contingency you would like to account " +
              "for autoscaling. Default value is 10%.")
    )
    parser.add_argument(
        "-m", "--months", default=1, type=int,
        help=("Number of months to calculate Azure credits for. Default value "
              + "is 1 month.")
    )

    return parser.parse_args()


def calculate_costs(billing_info):
    """
Function to calculate various monthly and yearly costs of the cluster and
container registry required to run a BinderHub. A contingency value is parsed
from the command line in order to account for autoscaling.

    :param billing_info: a dict object containing the billing information
    :param contingency: the desired contingency percentage (float, 0 < contingency < 1)
    :return: updated instance of billing_info (dict)
    """
    # Create empty dictionary
    billing_info["costs"] = {}

    # Calculate total VM cost per month
    billing_info["costs"]["cluster_cost_permonth_usd"] = (
        billing_info["cluster"]["cost_pernode_permonth_usd"] *
        billing_info["cluster"]["node_number"]
    )

    # Calculate ACR cost per year
    billing_info["costs"]["acr_cost_peryear_usd"] = (
        billing_info["acr"]["cost_perday_usd"] * 365.25
    )

    # Calculate average ACR cost per month
    billing_info["costs"]["acr_cost_peravgmonth_usd"] = (
        billing_info["costs"]["acr_cost_peryear_usd"] / 12
    )

    return billing_info


def summary_stats(yml, contingency, months):
    # Print cost breakdown
    if months != 1:
        print(f"""
Cluster cost per month: ${yml["costs"]["cluster_cost_permonth_usd"]:.2f}
ACR cost per month: ${yml["costs"]["acr_cost_peravgmonth_usd"]:.2f}

For {months} months:
Cluster cost per month: ${months * yml["costs"]["cluster_cost_permonth_usd"]:.2f}
ACR cost per month: ${months * yml["costs"]["acr_cost_peravgmonth_usd"]:.2f}

For {months} months with {contingency}% contingency:
Cluster cost per month: ${(1.0 + contingency) * months * yml["costs"]["cluster_cost_permonth_usd"]:.2f}
ACR cost per month: ${(1.0 + contingency) * months * yml["costs"]["acr_cost_peravgmonth_usd"]:.2f}

Total cost for {months} months with {contingency}% contingency:
${(1.0 + contingency) * months * (yml["costs"]["cluster_cost_permonth_usd"] + yml["costs"]["acr_cost_peravgmonth_usd"]):.2f}
""")

    else:
        print(f"""
Cluster cost per month: ${yml["costs"]["cluster_cost_permonth_usd"]:.2f}
ACR cost per month: ${yml["costs"]["acr_cost_peravgmonth_usd"]:.2f}

With {contingency}% contingency:
Cluster cost per month: ${(1.0 + contingency) * yml["costs"]["cluster_cost_permonth_usd"]:.2f}
ACR cost per month: ${(1.0 + contingency) * yml["costs"]["acr_cost_peravgmonth_usd"]:.2f}

Total cost with {contingency}% contingency:
${(1.0 + contingency) * (yml["costs"]["cluster_cost_permonth_usd"] + yml["costs"]["acr_cost_peravgmonth_usd"]):.2f}
""")


if __name__ == "__main__":
    # Parse command line args
    args = parse_args()
    contingency = float(args.contingency) / 100.0

    # Read in billing info
    with open("hub23_billing.yaml", 'r') as stream:
        try:
            billing_info = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Calculate costs
    billing_info = calculate_costs(billing_info)

    # Print Costs
    summary_stats(billing_info, args.contingency, args.months)
