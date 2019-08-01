import os
import argparse
import subprocess

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
    version
        String.
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
    cluster_name
        String.
    resource_group
        String.
    identity
        Boolean.
    """
    print("Logging into Azure")
    if identity:
        proc = subprocess.Popen(
            ["az", "login", "--identity"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        proc = subprocess.Popen(
            ["az", "login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    res = proc.communicate()
    if proc.returncode == 0:
        print("Successfully logged into Azure")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

    print(f"Setting kubectl context for: {cluster_name}")
    subprocess.check_call([
        "az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group
    ])

    print("Initialising Helm")
    subprocess.check_call([
        "helm", "init", "--client-only"
    ])

def main():
    args = parse_args()

    if args.dry_run:
        print("THIS IS A DRY-RUN. HELM CHART WILL NOT BE UPGRADED.")

    # Setup Azure
    azure_setup(args.cluster_name, args.resource_group, identity=args.identity)

    if args.version is None:
        # Find most recent deployed version
        version = find_version()

    # Pulling/updating Helm Chart repo
    print("Adding and updating JupyterHub/BinderHub Helm Chart")
    subprocess.check_call([
        "helm", "repo", "add", "jupyter", "https://jupyterhub.github.io/helm-chart"
    ])
    subprocess.check_call(["helm", "repo", "update"])

    # Helm Upgrade Command
    helm_upgrade_cmd = [
        "helm", "upgrade", args.hub_name, "jupyterhub/binderhub",
        f"--version={version}",
        "-f", os.path.join(".secret", "secret.yaml"),
        "-f", os.path.join(".secret", "config.yaml"),
        "--wait"
    ]
    if args.dry_run:
        helm_upgrade_cmd.append("--dry-run")
        print("Performing a dry-run helm upgrade")
    else:
        print("Upgrading helm chart")
    subprocess.check_call(helm_upgrade_cmd)

    # Print the pods
    subprocess.check_call([
        "kubectl", "get", "pods", "-n", args.hub_name
    ])

    # Fetching the Binder IP address
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
        print(f"Binder IP (binder.hub23.turing.ac.uk): {output}")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

if __name__ == "__main__":
    main()
