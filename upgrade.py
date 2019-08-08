import os
import logging
import argparse
from run_command import *

# Setup log config
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
        "-v",
        "--version",
        type=str,
        default=None,
        help="Helm Chart version to upgrade to. Optional."
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

def find_version():
    """Find the latest Helm Chart version deployed

    Returns
    -------
    version: string
    """
    from yaml import safe_load as load

    with open("changelog.txt", "r") as f:
        changelog = load(f)

    keys = list(changelog.keys())
    return changelog[keys[-1]]

def azure_setup(cluster_name, resource_group, identity=False):
    """Setup kubectl and helm to access BinderHub cluster

    Parameters
    ----------
    cluster_name: string
    resource_group: string
    identity: boolean
    """
    login_cmd = ["az", "login"]

    if identity:
        login_cmd.append("--identity")
        logging.info("Logging into Azure with a Managed System Identity")
    else:
        logging.info("Logging into Azure")

    result = run_cmd(login_cmd)
    if result["returncode"] == 0:
        logging.info("Successfully logged into Azure")
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    if not identity:
        logging.info(f"Setting kubectl context for: {cluster_name}")
        cmd = [
            "az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group
        ]
        result = run_cmd(cmd)
        if result["returncode"] == 0:
            logging.info(result["output"])
        else:
            logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

    logging.info("Initialising Helm")
    cmd = ["helm", "init", "--client-only"]
    result = run_cmd(cmd)
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

    if args.version is None:
        # Find most recent deployed version
        version = find_version()

    # Pulling/updating Helm Chart repo
    logging.info("Adding and updating JupyterHub/BinderHub Helm Chart")
    cmd = [
        "helm", "repo", "add", "jupyterhub", "https://jupyterhub.github.io/helm-chart"
    ]
    result = run_cmd(cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])

    cmd = ["helm", "repo", "update"]
    result = run_cmd(cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    # Helm Upgrade Command
    helm_upgrade_cmd = [
        "helm", "upgrade", args.hub_name, "jupyterhub/binderhub",
        "-f", os.path.join(".secret", "secret.yaml"),
        "-f", os.path.join(".secret", "config.yaml"),
        "--wait"
    ]

    if args.version is None:
        helm_upgrade_cmd.append(f"--version={version}")
    else:
        helm_upgrade_cmd.append(f"--version={args.version}")

    if args.dry_run:
        helm_upgrade_cmd.append("--dry-run")
        logging.info("Performing a dry-run helm upgrade")
    else:
        logging.info("Upgrading helm chart")

    result = run_cmd(helm_upgrade_cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    # Print the pods
    logging.info("Fetching the Kubernetes pods")
    cmd = ["kubectl", "get", "pods", "-n", args.hub_name]
    result = run_cmd(cmd)
    if result["returncode"] == 0:
        logging.info(result["output"])
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

    # Fetching the Binder IP address
    logging.info("Fetching the Binder IP address")
    kubectl_cmd = ["kubectl", "get", "svc", "binder", "-n", args.hub_name]
    awk_cmd = ["awk", "{ print $4}"]
    tail_cmd = ["tail", "-n", "1"]

    result = run_pipe_cmd([kubectl_cmd, awk_cmd, tail_cmd])
    if result["returncode"] == 0:
        logging.info(f"Binder IP: {result['output']}")
    else:
        logging.error(result["err_msg"])
        raise Exception(result["err_msg"])

if __name__ == "__main__":
    main()
