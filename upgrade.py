import os
import logging
import argparse
import subprocess

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

    proc = subprocess.Popen(
        login_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    res = proc.communicate()
    if proc.returncode == 0:
        logging.info("Successfully logged into Azure")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        logging.error(err_msg)
        raise Exception(err_msg)

    logging.info(f"Setting kubectl context for: {cluster_name}")
    subprocess.check_call([
        "az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group
    ])

    logging.info("Initialising Helm")
    output = subprocess.check_call(["helm", "init", "--client-only"])

def main():
    args = parse_args()

    if args.dry_run:
        logging.info("THIS IS A DRY-RUN. HELM CHART WILL NOT BE UPGRADED.")

    # Setup Azure
    azure_setup(args.cluster_name, args.resource_group, identity=args.identity)

    # Updating local chart
    logging.info(f"Updating local chart dependencies: {args.chart_name}")
    os.chdir(args.chart_name)
    subprocess.check_call(["helm", "dependency", "update"])
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
    subprocess.check_call(helm_upgrade_cmd)

    # Print the pods
    logging.info(f"Printing pod status for: {args.hub_name}")
    subprocess.check_call([
        "kubectl", "get", "pods", "-n", args.hub_name
    ])

    # Fetching the Binder IP address
    logging.info("Fetching IP addresses")
    kubectl_cmd = ["kubectl", "get", "svc", "binder", "-n", args.hub_name]
    awk_cmd = ["awk", "{ print $4}"]
    tail_cmd = ["tail", "-n", "1"]

    p1 = subprocess.Popen(kubectl_cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(awk_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(tail_cmd, stdin=p2.stdout, stdout=subprocess.PIPE)
    p2.stdout.close()

    res = p3.communicate()
    if p3.returncode == 0:
        output = res[0].decode(encoding="utf-8")
        logging.info(f"Binder IP: {output}")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        logging.error(err_msg)
        raise Exception(err_msg)

if __name__ == "__main__":
    main()
