import yaml
import argparse
import datetime


def parse_args():
    """
Parse command line arguments.

This function reads one command line argument which is the percentage contingency
desired when calculating costs for autoscaling of the cluster. If not provided,
this value defaults to 10%.
    """
    parser = argparse.ArgumentParser(
        description="Parse a contingency percentage for calculating BinderHub Cloud costs."
    )

    parser.add_argument("-c", "--contingency", default=10,
                        help="Parse the percentage contingency you would like to account for "
                             "autoscaling. Default value is 10%.")

    return parser.parse_args()


def calculate_costs(billing_info, contingency):
    """
Function to calculate various monthly and yearly costs of the cluster and container
registry required to run a BinderHub. A contingency value is parsed from the
command line in order to account for autoscaling.
    :param billing_info:
    :param contingency:
    :return:
    """
    # Time stamp the calculations
    billing_info["datetime_calculated_utc"] = "{0}".format(datetime.datetime.utcnow())

    # Calculate total VM cost per month
    billing_info["cluster"]["cost_permonth_usd"] = (
        billing_info["cluster"]["cost_pernode_permonth_usd"] *
        billing_info["cluster"]["node_number"]
    )

    # Calculate total VM cost per year
    billing_info["cluster"]["cost_peryear_usd"] = (
        billing_info["cluster"]["cost_permonth_usd"] * 12
    )

    # Calculate ACR cost per year
    billing_info["acr"]["cost_peryear_usd"] = (
        billing_info["acr"]["cost_perday_usd"] * 365.25
    )

    # Calculate average ACR cost per month
    billing_info["acr"]["cost_peravgmonth_usd"] = (
        billing_info["acr"]["cost_peryear_usd"] / 12
    )

    # Calculate monthly costs
    billing_info["costs_usd"] = {"monthly":
        billing_info["cluster"]["cost_permonth_usd"] +
        billing_info["acr"]["cost_peravgmonth_usd"]
    }

    # Calculate yearly costs
    billing_info["costs_usd"]["yearly"] = (
        billing_info["cluster"]["cost_peryear_usd"] +
        billing_info["acr"]["cost_peryear_usd"]
    )

    # Calculate monthly costs with contingency
    billing_info["costs_usd"]["monthly_contingency"] = (
        billing_info["costs_usd"]["monthly"] * (1.0 + contingency)
    )

    # Calculate yearly costs with contingency
    billing_info["costs_usd"]["yearly_contingency"] = (
        billing_info["costs_usd"]["yearly"] * (1.0 + contingency)
    )

    return billing_info


def summary_stats(yml, contingency):
    # Print cost breakdown
    print("""
Total yearly cost (no contingency): ${0:.2f}
Total yearly cost with {1}% contingency: ${2:.2f} ** PASTE THIS VALUE INTO TOPDESK **
""".format(
        yml["costs_usd"]["yearly"], contingency,
        yml["costs_usd"]["yearly_contingency"]
    ))


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

    # # Calculate costs
    billing_info = calculate_costs(billing_info, contingency)
    print(billing_info)

    # Print Costs
    summary_stats(billing_info, args.contingency)

    # Output calculations
    with open("hub23_billing_calc.yaml", "w") as stream:
        yaml.dump(billing_info, stream)
