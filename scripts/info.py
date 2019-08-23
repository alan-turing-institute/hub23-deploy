import argparse
import subprocess
from run_command import *

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

class HubInfo(object):
    def __init__(self, argsDict):
        self.hub_name = argsDict["hub_name"]
        self.cluster_name = argsDict["cluster_name"]
        self.resource_group = argsDict["resource_group"]
        self.identity = argsDict["identity"]

    def get_info(self):
        self.login()

        ip_addresses = {}
        kubectl_cmd = ["kubectl", "-n", self.hub_name, "get", "svc"]
        awk_cmd = ["awk", "{ print $4}"]
        tail_cmd = ["tail", "-n", "1"]

        for svc in ["proxy-public", "binder"]:
            new_cmd = kubectl_cmd + [svc]
            result = run_pipe_cmd([new_cmd, awk_cmd, tail_cmd])
            if result["returncode"] == 0:
                ip_addresses[svc] = result["output"].strip("\n")
            else:
                raise Exception(result["err_msg"])

        print(f"JupyterHub IP: {ip_addresses['proxy-public']}\nBinder IP: {ip_addresses['binder']}")

    def login(self):
        login_cmd = ["az", "login"]

        if self.identity:
            login_cmd.append("--identity")

        result = run_cmd(login_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        cred_cmd = [
            "az", "aks", "get-credentials", "-n", self.cluster_name, "-g",
            self.resource_group
        ]
        result = run_cmd(cred_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

if __name__ == "__main__":
    args = parse_args()
    bot = HubInfo(vars(args))
    bot.get_info()
