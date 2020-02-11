from subprocess import check_output
from .run_command import run_cmd, run_pipe_cmd


class Hub:
    """Class for interacting with a BinderHub"""

    def __init__(self, argsDict):
        """Constructor for Hub class"""
        for k, v in argsDict.items():
            setattr(self, k, v)

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

    def pull_secrets(self):
        """Pull secrets from an Azure Key Vault

        Returns:
            Dict -- A dictionary containing the pulled secrets
        """
        self.login()

        # Secrets to be pulled
        secret_names = [
            "apiToken",
            "secretToken",
            "github-client-id",
            "github-client-secret",
            "SP-appID",
            "SP-key",
            "binderhub-access-token",
        ]
        secrets = {}

        # Pull the secrets
        for secret in secret_names:
            value = check_output(
                [
                    "az",
                    "keyvault",
                    "show",
                    "-n",
                    secret,
                    "--vault-name",
                    self.vault_name,
                    "--query",
                    "value",
                    "--output",
                    "tsv",
                ]
            )

            secrets[secret] = value

        return secrets
