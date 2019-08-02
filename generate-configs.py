import os
import json
import argparse
from run_command import run_cmd
from subprocess import check_output

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to generate configuration files for a BinderHub deployment"
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
        "-o",
        "--org-name",
        type=str,
        default="binderhub-test-org",
        help="GitHub organisation name for authentication"
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

    return parser.parse_args()

def get_secrets(vault_name, identity=False):
    """Get secrets from Azure key vault

    Parameters
    ----------
    vault_name
        String.
    identity
        Boolean.

    Returns
    -------
    secrets
        Dictionary.
    """
    secret_names = [
        "apiToken",
        "secretToken",
        "binderhub-access-token",
        "github-client-id",
        "github-client-secret",
        "SP-appID",
        "SP-key"
    ]

    secrets = {}

    # Login to Azure
    login_cmd = ["az", "login"]
    if identity:
        login_cmd.append("--identity")
        print("Logging into Azure with a Managed System Identity")
    else:
        print("Login to Azure")

    result = run_cmd(login_cmd)
    if result["returncode"] == 0:
        print("Successfully logged into Azure")
    else:
        raise Exception(result["err_msg"])

    # Get secrets
    for secret in secret_names:
        print(f"Pulling secret: {secret}")
        # Get secret information and convert to json
        json_out = check_output([
            "az", "keyvault", "secret", "show", "-n", secret,
            "--vault-name", vault_name
        ]).decode(encoding="utf-8")
        secret_info = json.loads(json_out)

        # Save secret to dictionary
        secrets[secret] = secret_info["value"]

    return secrets

def main():
    args = parse_args()

    # Make a secrets folder
    secret_dir = ".secret"
    if not os.path.exists(secret_dir):
        print(f"Creating directory: {secret_dir}")
        os.mkdir(secret_dir)
        print(f"Created directory: {secret_dir}")
    else:
        print(f"Directory already exists: {secret_dir}")

    secrets = get_secrets(args.vault_name, args.identity)

    print("Generating configuration files")
    for filename in ["config", "secret"]:
        print(f"Reading template file for: {filename}")

        with open(f"{filename}-template.yaml", "r") as f:
            template = f.read()

        if filename == "config":
            template = template.format(
                registry_name=args.registry_name,
                image_prefix=args.image_prefix,
                jupyterhub_ip=args.jupyterhub_ip,
                binder_ip=args.binder_ip,
                github_client_id=secrets["github-client-id"],
                github_client_secret=secrets["github-client-secret"],
                org_name=args.org_name
            )

        elif filename == "secret":
            template = template.format(
                apiToken=secrets["apiToken"],
                secretToken=secrets["secretToken"],
                registry_name=args.registry_name,
                username=secrets["SP-appID"],
                password=secrets["SP-key"],
                accessToken=secrets["binderhub-access-token"]
            )
        else:
            raise FileNotFoundError("Unknown file")

        print(f"Writing YAML file for: {filename}")
        with open(os.path.join(secret_dir, f"{filename}.yaml"), "w") as f:
            f.write(template)

    print(f"BinderHub files have been configured: {os.listdir(secret_dir)}")

if __name__ == "__main__":
    main()
