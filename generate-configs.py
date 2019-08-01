import os
import json
import argparse
import subprocess

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
        "SP-appID",
        "SP-key"
    ]

    secrets = {}

    # Login to Azure
    print("Logging into Azure")
    if identity:
        proc = subprocess.Popen(
            ["az", "login", "--identity"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        proc = subprocess.Popen(
            ["az", "login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    res = proc.communicate()
    if proc.returncode == 0:
        print("Successfully logged into Azure")
    else:
        err_msg = res[1].decode(encoding="utf-8")
        raise Exception(err_msg)

    # Get secrets
    for secret in secret_names:
        print(f"Pulling secret: {secret}")
        # Get secret information and convert to json
        json_out = subprocess.check_output([
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
    for filename in ["prod"]:
        print(f"Reading template file for: {filename}")

        with open(f"{filename}-template.yaml", "r") as f:
            template = f.read()

        template = template.format(
            apiToken=secrets["apiToken"],
            secretToken=secrets["secretToken"],
            username=secrets["SP-appID"],
            password=secrets["SP-key"]
        )

        print(f"Writing YAML file for: {filename}")
        with open(os.path.join(secret_dir, f"{filename}.yaml"), "w") as f:
            f.write(template)

    print(f"BinderHub files have been configured: {os.listdir(secret_dir)}")

if __name__ == "__main__":
    main()
