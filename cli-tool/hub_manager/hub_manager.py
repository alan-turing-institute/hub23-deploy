import os
import logging

from subprocess import check_output
from .run_command import run_cmd, run_pipe_cmd


class HubManager:
    """Class for interacting with a BinderHub"""

    def __init__(self, argsDict):
        """Constructor for Hub class"""
        self.chart_name = "hub23-chart"
        self.cluster_name = "hub23cluster"
        self.hub_name = "hub23"
        self.resource_group = "Hub23"
        self.subscription = "Turing-BinderHub"
        self.vault_name = "hub23-keyvault"

        for k, v in argsDict.items():
            setattr(self, k, v)

        # Get working directory
        self.get_cwd()

        if self.verbose:
            # Enable verbose output
            self.logging_config()

    def generate_config_files(self):
        """Generate configuration files for BinderHub"""
        secrets = self.pull_secrets()
        self.check_filepaths()

        if self.verbose:
            logging.info("Generating config files")

        # Generate config files
        for filename in ["prod"]:
            if self.verbose:
                logging.info("Reading template file for: %s" % filename)
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

            if self.verbose:
                logging.info("Writing YAML file for: %s" % filename)
            with open(
                os.path.join(self.secret_dir, f"{filename}.yaml"), "w"
            ) as f:
                f.write(template)

            if self.verbose:
                logging.info(
                    "Secret BinderHub files have been configured: %s"
                    % os.listdir(self.secret_dir)
                )

    def get_logs(self):
        """Return the logs of the JupyterHub Pod"""
        self.login()
        self.configure_azure()

        if self.pod == "jupyterhub":
            if self.verbose:
                logging.info(
                    "Pulling JupyterHub pod logs for: %s" % self.hub_name
                )
            regex = "^hub-"
        elif self.pod == "binder":
            if self.verbose:
                logging.info("Pulling Binder pod logs for: %s" % self.hub_name)
            regex = "^binder-"
        else:
            raise ValueError(
                "Unrecognised pod type. Expecting either jupyterhub or binder"
            )

        kubectl_cmd = [
            "kubectl",
            "get",
            "pods",
            "-n",
            self.hub_name,
            "-o=jsonpath='{.items[*].metadata.name}'",
        ]
        tr_cmd = ["tr", "' '", "'\n'"]
        grep_cmd = ["grep", regex]

        result = run_pipe_cmd([kubectl_cmd, tr_cmd, grep_cmd])
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        log_cmd = ["kubectl", "logs", result["output"], "-n", self.hub_name]
        result = run_cmd(log_cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        print(result["output"])

    def helm_upgrade(self):
        """Perform upgrade of the helm chart"""
        self.login()
        self.configure_azure()
        self.helm_init()
        self.check_filepaths()
        self.generate_config_files()
        self.update_local_chart()

        helm_upgrade_cmd = [
            "helm",
            "upgrade",
            self.hub_name,
            f"./{self.chart_name}",
            "-f",
            os.path.join(self.deploy_dir, "prod.yaml"),
            "-f",
            os.path.join(self.folder, self.secret_dir, "prod.yaml"),
            "--wait",
            "--install",
        ]

        if self.dry_run:
            if self.verbose:
                logging.info(
                    "THIS IS A DRY-RUN. HELM CHART WILL NOT BE UPGRADED."
                )
            helm_upgrade_cmd.append("--dry-run")

        if self.debug:
            if self.verbose:
                logging.info("Debug option enabled for helm upgrade")
            helm_upgrade_cmd.append("--debug")

        result = run_cmd(helm_upgrade_cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        self.print_pods()

    def print_pods(self):
        """Print the Kubernetes pods"""
        if self.verbose:
            logging.info(
                "Fetching the Kubernetes pods for: %s" % self.hub_name
            )

        if self.action == "print-pods":
            self.login()
            self.configure_azure()

        cmd = ["kubectl", "get", "pods", "-n", self.hub_name]
        result = run_cmd(cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        print(result["output"])

    def check_filepaths(self):
        """Set filepaths and create secret directory"""
        if self.verbose:
            logging.info("Constructing filepaths")

        self.deploy_dir = os.path.join(self.folder, "deploy")
        self.secret_dir = os.path.join(self.folder, ".secret")

        # Create the secrets folder
        if not os.path.exists(self.secret_dir):
            if self.verbose:
                logging.info("Creating directory: %s" % self.secret_dir)
                os.mkdir(self.secret_dir)
                logging.info("Created directory")
            else:
                os.mkdir(self.secret_dir)
        else:
            if self.verbose:
                logging.info("Directory already exists: %s" % self.secret_dir)
            pass

    def configure_azure(self):
        """Set Azure subscription and Kubernetes context"""
        if self.verbose:
            logging.info("Setting Azure subscription: %s" % self.subscription)

        sub_cmd = ["az", "account", "set", "--subscription"]

        if " " in self.subscription:
            sub_cmd.append(f'"{self.subscription}"')
        else:
            sub_cmd.append(self.subscription)

        result = run_cmd(sub_cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        if self.verbose:
            logging.info("Successfully set Azure subscription")
            logging.info("Setting kubectl contect for: %s" % self.cluster_name)

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
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        if self.verbose:
            logging.info(result["output"])

    def helm_init(self):
        """Initialise helm"""
        if self.verbose:
            logging.info("Initialising helm")

        cmd = ["helm", "init", "--client-only"]
        result = run_cmd(cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        if self.verbose:
            logging.info(result["output"])

    def logging_config(self):
        """Set logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_cwd(self):
        """Get working directory"""
        cwd = os.getcwd()

        if cwd.endswith("cli-tool"):
            tmp = cwd.split("/")
            del tmp[-1]
            cwd = "/".join(tmp)

        self.folder = cwd

    def login(self):
        """Login to Azure"""
        login_cmd = ["az", "login"]

        if self.identity:
            if self.verbose:
                logging.info(
                    "Logging into Azure with a Managed System Identity"
                )
            login_cmd.append("--identity")
        else:
            if self.verbose:
                logging.info("Logging into Azure")
            pass

        result = run_cmd(login_cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        if self.verbose:
            logging.info("Successfully logged into Azure")

    def pull_secrets(self):
        """Pull secrets from an Azure Key Vault

        Returns:
            Dict -- A dictionary containing the pulled secrets
        """
        self.login()

        if self.verbose:
            logging.info("Pulling secrets from: %s" % self.vault_name)

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
            if self.verbose:
                logging.info("Pulling secret: %s" % secret)

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

    def update_local_chart(self):
        """Update the local helm chart"""
        if self.verbose:
            logging.info(
                "Updating local helm chart dependencies for: %s"
                % self.chart_name
            )

        os.chdir(os.path.join(self.folder, self.chart_name))
        update_cmd = ["helm", "dep", "up"]
        result = run_cmd(update_cmd)
        if result["returncode"] != 0:
            if self.verbose:
                logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

        if self.verbose:
            logging.info(result["output"])

        os.chdir(os.pardir)
