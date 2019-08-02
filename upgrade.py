import os
import logging
import argparse
from run_command import *
from subprocess import check_call

# Setup logging config
logging.basicConfig(
    level=logging.DEBUG,
    filename="upgrade.log",
    filemode="a",
    format="[%(asctime)s %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to upgrade a helm chart for a BinderHub deployment on Azure"
    )

    parser.add_argument(
        "-n",
        "--hub-name",
        type=str,
        default="hub23",
        help="BinderHub name/Helm release name"
    )
    parser.add_argument(
        "-z",
        "--chart-name",
        type=str,
        default="hub23-chart",
        help="Local Helm Chart name"
    )
    parser.add_argument(
        "-c",
        "--cluster-name",
        type=str,
        default="hub23cluster",
        help="Name of Azure Kubernetes Service"
    )
    parser.add_argument(
        "-g",
        "--resource-group",
        type=str,
        default="Hub23",
        help="Azure Resource Group"
    )
    parser.add_argument(
        "--identity",
        action="store_true",
        help="Login to Azure using a Managed System Identity"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Performs a dry-run upgrade of the Helm Chart"
    )

    return parser.parse_args()

def azure_setup(cluster_name, resource_group, identity=False):
    """Setup kubectl and helm to access BinderHub cluster

    Parameters
    ----------
    cluster_name
        String.
    resource_group
        String.
    identity
        Boolean.
    """
    login_cmd = ["az", "login"]
    if identity:
        login_cmd.append("--identity")
        logging.info("Login to Azure with Managed System Identity")
    else:
        logging.info("Login to Azure")

    result = run_cmd(login_cmd)
    if result["returncode"] == 0:
        logging.info("Successfully logged into Azure")
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    aks_cmd = ["az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group]
    logging.info(f"Setting kubectl context for: {cluster_name}")
    result = run_cmd(aks_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    helm_cmd = ["helm", "init", "--client-only"]
    logging.info("Initialising Helm")
    result = run_cmd(helm_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

def main():
    args = parse_args()

    if args.dry_run:
        logging.info("THIS IS A DRY-RUN. HELM CHART WILL NOT BE UPGRADED.")

    # Setup Azure
    azure_setup(args.cluster_name, args.resource_group, identity=args.identity)

    # Updating local chart
    logging.info(f"Updating local chart dependencies: {args.chart_name}")
    os.chdir(args.chart_name)

    update_cmd = ["helm", "dependency", "update"]
    result = run_cmd(update_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    os.chdir(os.pardir)

    # Helm Upgrade Command
    helm_upgrade_cmd = [
        "helm", "upgrade", args.hub_name, args.chart_name,
        "-f", os.path.join("deploy", "prod.yaml"),
        "-f", os.path.join(".secret", "prod.yaml"),
        "--wait"
    ]

    if args.dry_run:
        helm_upgrade_cmd.append("--dry-run")
        logging.info(f"Performing a dry-run helm upgrade for: {args.hub_name}")
    else:
        logging.info(f"Upgrading helm chart for: {args.hub_name}")

    result = run_cmd(helm_upgrade_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    # Print the pods
    logging.info(f"Printing pod status for: {args.hub_name}")
    pod_cmd = ["kubectl", "get", "pods", "-n", args.hub_name]
    result = run_cmd(pod_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    # Fetching the Binder IP address
    logging.info("Fetching IP address")
    kubectl_cmd = ["kubectl", "get", "svc", "binder", "-n", args.hub_name]
    awk_cmd = ["awk", "{ print $4}"]
    tail_cmd = ["tail", "-n", "1"]

    result = run_pipe_cmd([kubectl_cmd, awk_cmd, tail_cmd])
    if result["returncode"] == 0:
        print(f"Binder IP: {result['output']}")
    else:
        raise Exception(result["err_msg"])

if __name__ == "__main__":
    main()
