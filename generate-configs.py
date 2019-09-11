import os
import sys
import json
import logging
import argparse
from subprocess import check_output
from HubClass.run_command import run_cmd

# Setup logging config
logging.basicConfig(
    level=logging.DEBUG,
    filename="generate-configs.log",
    filemode="a",
    format="[%(asctime)s %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to generate configuration files for a BinderHub deployment"
    )

    parser.add_argument(
        "-s",
        "--subscription",
        type=str,
        default="Turing-BinderHub",
        help="Azure Subscription where Key Vault is located"
    )
    parser.add_argument(
        "-v",
        "--vault-name",
        type=str,
        default="hub23-keyvault",
        help="Name of the Azure Key Vault where secrets are stored"
    )
    parser.add_argument(
        "-r",
        "--registry-name",
        type=str,
        default="hub23registry",
        help="Name of the Azure Container Service to connect to the BinderHub"
    )
    parser.add_argument(
        "-p",
        "--image-prefix",
        type=str,
        default="hub23/binder-dev",
        help="Image prefix to prepend to Docker images"
    )
    parser.add_argument(
        "-j",
        "--jupyterhub-ip",
        type=str,
        default="hub.hub23.turing.ac.uk",
        help="IP address of the JupyterHub"
    )
    parser.add_argument(
        "-b",
        "--binder-ip",
        type=str,
        default="binder.hub23.turing.ac.uk",
        help="IP address of the Binder page"
    )
    parser.add_argument(
        "--identity",
        action="store_true",
        help="Login to Azure using a Managed System Identity"
    )
    parser.add_argument(
        "--sp-login",
        action="store_true",
        help="Login in to Azure using a Service Principal"
    )
    parser.add_argument(
        "--sp-app-id",
        type=str,
        default="",
        required="--sp-login" in sys.argv,
        help="App ID of an Azure Service Principal"
    )
    parser.add_argument(
        "--sp-key",
        type=str,
        default="",
        required="--sp-login" in sys.argv,
        help="Key of an Azure Service Principal"
    )

    return parser.parse_args()

class GenerateConfigFiles(object):
    def __init__(self, argsDict):
        self.subscription = argsDict["subscription"]
        self.vault_name = argsDict["vault_name"]
        self.registry_name = argsDict["registry_name"]
        self.image_prefix = argsDict["image_prefix"]
        self.jupyterhub_ip = argsDict["jupyterhub_ip"]
        self.binder_ip = argsDict["binder_ip"]
        self.identity = argsDict["identity"]
        self.sp_login = argsDict["sp_login"]
        self.sp_app_id = argsDict["sp_app_id"]
        self.sp_key = argsDict["sp_key"]

        self.get_secrets()

    def login(self):
        # Login to Azure
        login_cmd = ["az", "login"]

        if self.identity:
            login_cmd.append("--identity")
            logging.info("Logging into Azure with a Managed System Identity")

        elif self.sp_login:
            tenant_id = check_output([
                "az", "account", "show", "-s", self.subscription, "--query",
                "tenantId", "-o", "tsv"
            ]).decode(encoding="utf8").strip("\n")

            login_cmd.extend([
                "--service-principal", "-u", self.sp_app_id, "-p", self.sp_key,
                "--tenant", tenant_id
            ])
            logging.info("Logging into Azure with Service Principal")

        else:
            logging.info("Login to Azure")

        result = run_cmd(login_cmd)
        if result["returncode"] == 0:
            logging.info("Successfully logged into Azure")
        else:
            logging.error(result["err_msg"])
            raise Exception(result["err_msg"])

    def get_secrets(self):
        self.login()

        secret_names = [
            "apiToken",
            "secretToken",
            "github-client-id",
            "github-client-secret",
            "SP-appID",
            "SP-key"
        ]

        self.secrets = {}

        # Get secrets
        for secret in secret_names:
            logging.info(f"Pulling secret: {secret}")
            # Get secret information and convert to json
            value = check_output([
                "az", "keyvault", "secret", "show", "-n", secret,
                "--vault-name", self.vault_name, "--query", "value", "-o",
                "tsv"
            ]).decode(encoding="utf8").strip("\n")

            # Save secret to dictionary
            self.secrets[secret] = value

    def generate_config_files(self):
        # Make a secrets folder
        deploy_dir = "deploy"
        secret_dir = ".secret"
        if not os.path.exists(secret_dir):
            logging.info(f"Creating directory: {secret_dir}")
            os.mkdir(secret_dir)
            logging.info(f"Created directory: {secret_dir}")
        else:
            logging.info(f"Directory already exists: {secret_dir}")

        logging.info("Generating configuration files")
        for filename in ["prod"]:
            logging.info(f"Reading template file for: {filename}")

            with open(f"{deploy_dir}/{filename}-template.yaml", "r") as f:
                template = f.read()

            template = template.format(
                apiToken=self.secrets["apiToken"],
                secretToken=self.secrets["secretToken"],
                username=self.secrets["SP-appID"],
                password=self.secrets["SP-key"],
                github_client_id=self.secrets["github-client-id"],
                github_client_secret=self.secrets["github-client-secret"]
            )

            logging.info(f"Writing YAML file for: {filename}")
            with open(os.path.join(secret_dir, f"{filename}.yaml"), "w") as f:
                f.write(template)

        logging.info(f"BinderHub files have been configured: {os.listdir(secret_dir)}")

if __name__ == "__main__":
    args = parse_args()

    if args.identity and args.sp_login:
        raise Exception("Please provide EITHER --identity OR --sp-login flag")

    bot = GenerateConfigFiles(vars(args))
    bot.generate_config_files()
