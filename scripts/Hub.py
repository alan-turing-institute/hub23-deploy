from run_command import *

class Hub(object):
    def __init__(self, argsDict):
        self.hub_name = argsDict["hub_name"]
        self.cluster_name = argsDict["cluster_name"]
        self.resource_group = argsDict["resource_group"]
        self.identity = argsDict["identity"]

    def login(self):
        login_cmd = ["az", "login"]

        if identity:
            login_cmd.append("--identity")

        result = run_cmd(login_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        creds_cmd
        subprocess.check_call([
            "az", "aks", "get-credentials", "-n", cluster_name, "-g", resource_group
        ])

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

    def get_logs(self):
        self.login()

        kubectl_cmd = ["kubectl", "get", "pods", "-n", seldf.hub_name,
                   "-o=jsonpath='{.items[*].metadata.name}'"]
        tr_cmd = ["tr", "' '", "'\n'"]
        grep_cmd = ["grep", "^hub-"]

        result = run_pipe_cmd([kubectl_cmd, tr_cmd, grep_cmd])
        if result["returncode"] == 0:
            hub_pod = result["output"].strip("\n")
        else:
            raise Exception(result["err_msg"])

        log_cmd = ["kubectl", "logs", hub_pod, "-n", self.hub_name]
        result = run_cmd(log_cmd)
        if result["returncode"] == 0:
            print(result["output"])
        else:
            raise Exception(result["err_msg"])
