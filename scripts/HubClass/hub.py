from .run_command import run_cmd, run_pipe_cmd


class Hub:
    """Functions for interacting with BinderHub"""

    def __init__(self, argsDict):
        """Set arguments as variables"""
        self.hub_name = argsDict["hub_name"]
        self.cluster_name = argsDict["cluster_name"]
        self.resource_group = argsDict["resource_group"]
        self.identity = argsDict["identity"]

    def login(self):
        """Login to Azure"""
        login_cmd = ["az", "login"]

        if self.identity:
            login_cmd.append("--identity")

        result = run_cmd(login_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        cred_cmd = [
            "az",
            "aks",
            "get-credentials",
            "-n",
            self.cluster_name,
            "-g",
            self.resource_group,
        ]
        result = run_cmd(cred_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

    def get_logs(self):
        """Return the logs of the JupyterHub Pod"""
        self.login()

        kubectl_cmd = [
            "kubectl",
            "get",
            "pods",
            "-n",
            self.hub_name,
            "-o=jsonpath='{.items[*].metadata.name}'",
        ]
        tr_cmd = ["tr", "' '", "'\n'"]
        grep_cmd = ["grep", "^hub-"]

        result = run_pipe_cmd([kubectl_cmd, tr_cmd, grep_cmd])
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        hub_pod = result["output"].strip("\n")

        log_cmd = ["kubectl", "logs", hub_pod, "-n", self.hub_name]
        result = run_cmd(log_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        print(result["output"])
