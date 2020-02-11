import os
import logging

from subprocess import check_output
from .run_command import run_cmd, run_pipe_cmd


class Hub:
    """Class for interacting with a BinderHub"""

    def __init__(self, argsDict):
        """Constructor for Hub class"""
        for k, v in argsDict.items():
            setattr(self, k, v)

        self.get_cwd()

        if self.verbose:
            self.logging_config()

    def generate_config_files(self):
        """Generate configuration files for BinderHub"""
        secrets = self.pull_secrets()
        self.check_filepaths()

        # Generate config files
        for filename in ["prod"]:
            with open(
                os.path.join(self.deploy_dir, f"{filename}-template.yaml"), "r"
            ) as f:
                template = f.read()

            template = template.format(
                binderhub_access_token=secrets["binderhub-access-token"],
                username=secrets["SP-appID"],
                password=secrets["SP-key"],
                apiToken=secrets["apiToken"],
                secretToken=secrets["secretToken"],
                github_client_id=secrets["github-client-id"],
                github_client_secret=secrets["github-client-secret"],
            )

            with open(
                os.path.join(self.secret_dir, f"{filename}.yaml"), "w"
            ) as f:
                f.write(template)

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

    def helm_upgrade(self):
        self.login()
        self.configure_azure()
        self.helm_init

    def check_filepaths(self):
        """Set filepaths and create secret directory"""
        self.deploy_dir = os.path.join(self.folder, "deploy")
        self.secret_dir = os.path.join(self.folder, ".secret")

        # Create the secrets folder
        if not os.path.exists(self.secret_dir):
            os.mkdir(self.secret_dir)

    def configure_azure(self):
        """Set Azure subscription and Kubernetes context"""
        sub_cmd = ["az", "account", "set", "--subscription"]

        if " " in self.subscription:
            sub_cmd.append(f'"{self.subscription}"')
        else:
            sub_cmd.append(self.subscription)

        result = run_cmd(sub_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

        k8s_cmd = [
            "az",
            "aks",
            "get-credentials",
            "-n",
            self.cluster_name,
            "-g",
            self.resource_group,
        ]
        result = run_cmd(k8s_cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

    def helm_init(self):
        """Initialise helm"""
        cmd = ["helm", "init", "--client-only"]
        result = run_cmd(cmd)
        if result["returncode"] != 0:
            raise Exception(result["err_msg"])

    def logging_config(self):
        """Set logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_cwd():
        cwd = os.getcwd()

        if cwd.endswith("scripts"):
            tmp = cwd.split("/")
            del tmp[-1]
            cwd = "/".join(tmp)

        self.folder = cwd

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
