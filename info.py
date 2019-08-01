import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to print the IP addresses of the JupyterHub and Binder page"
    )

    parser.add_argument(
        "-n",
        "--hub-name",
        type=str,
        default="hub23",
        help="BinderHub name"
    )
    parser.add_argument(
        "-c",
        "--cluster_name",
        type=str,
        default="hub23cluster",
        help="Azure Kubernetes cluster name"
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

    return parser.parse_args()

def azure_setup(cluster_name, resource_group, identity=False):
    """Login to Azure and connect to Kubernetes cluster

    Parameters
    ----------
    cluster_name
        String.
    resource_group
        String.
    identity
        Boolean
    """
    login_cmd = ["az", "login"]

    if identity:
        login_cmd.append("--identity")

    print("Login to Azure")
    proc = subprocess.Popen(
        login_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    res = proc.communicate()
    if proc.returncode == 0:
        print("Successfully logged in to Azure")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

    print(f"Merging kubectl context for cluster: {cluster_name}")
    subprocess.check_call(
        ["az", "aks", "get-credentials", "-n", cluster_name, "-g",
         resource_group],
    )

def main():
    args = parse_args()

    azure_setup(args.cluster_name, args.resource_group, identity=args.identity)

    ip_addresses = {}
    kubectl_cmd = ["kubectl", "-n", args.hub_name, "get", "svc"]
    awk_cmd = ["awk", "{ print $4}"]
    tail_cmd = ["tail", "-n", "1"]

    for svc in ["proxy-public", "binder"]:
        print(f"Fetching IP address for: {svc}")

        new_cmd = kubectl_cmd + [svc]

        p1 = subprocess.Popen(new_cmd, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(awk_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        p3 = subprocess.Popen(tail_cmd, stdin=p2.stdout, stdout=subprocess.PIPE)
        p2.stdout.close()

        res = p3.communicate()
        if p3.returncode == 0:
            ip = res[0].decode(encoding="utf-8")
            ip_addresses[svc] = ip
        else:
            err_msg = res[1].decode(encoding="utf-8")
            raise Exception(err_msg)

    print(f"""
    JupyterHub IP: {ip_addresses['proxy-public']}
    Binder IP: {ip_addresses['binder']}
    """)

if __name__ == "__main__":
    main()
