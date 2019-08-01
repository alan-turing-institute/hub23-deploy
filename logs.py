import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to print the JupyterHub logs to the terminal"
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
        "--cluster-name",
        type=str,
        default="hub23cluster",
        help="Azure Kubernetes cluster name"
    )
    parser.add_argument(
        "-g",
        "--resource_group",
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
    """Configuring Azure to connect kubectl to the resources underpinning the BinderHub

    Parameters
    ----------
    cluster_name
        String.
    resource_group
        String.
    identity
        Boolean.
    """
    if identity:
        login_cmd = ["az", "login", "--identity"]
    else:
        login_cmd = ["az", "login"]

    print("Login to Azure")
    proc = subprocess.Popen(
        login_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    res = proc.communicate()
    if proc.returncode == 0:
        print("Successfully logged into Azure")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

    print(f"Merging kubectl context for cluster: {cluster_name}")
    subprocess.check_call([
        "az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group
    ])

def main():
    args = parse_args()

    azure_setup(args.cluster_name, args.resource_group, identity=args.identity)

    print("Fetching JupyterHub logs")
    kubectl_cmd = ["kubectl", "get", "pods", "-n", args.hub_name,
                   "-o=jsonpath='{.items[*].metadata.name}'"]
    tr_cmd = ["tr", "' '", "'\n'"]
    grep_cmd = ["grep", "^hub-"]

    p1 = subprocess.Popen(kubectl_cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(tr_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(grep_cmd, stdin=p2.stdout, stdout=subprocess.PIPE)
    p2.stdout.close()

    res = p3.communicate()
    print(res)
    if p3.returncode == 0:
        hub_pod = res[0].decode(encoding="utf-8").strip("\n")
        print(f"Hub pod: {hub_pod}")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

    subprocess.check_call([
        "kubectl", "logs", hub_pod, "-n", args.hub_name
    ])

if __name__ == "__main__":
    main()
