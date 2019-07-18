import os
import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        type=str,
        default=None,
        help="Helm Chart version to upgrade to"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    subprocess.check_call([
        "helm", "repo", "add", "jupyter", "https://jupyterhub.github.io/helm-chart"
    ])
    subprocess.check_call(["helm", "repo", "update"])

    subprocess.check_call([
        "helm", "upgrade", "hub23", "jupyterhub/binderhub",
        f"--version={args.version}",
        "-f", os.path.join(".secret", "secret.yaml"),
        "-f", os.path.join(".secret", "config.yaml")
    ])

    subprocess.check_call([
        "kubectl", "get", "pods", "-n", "hub23"
    ])
    output = subprocess.check_output([
        "kubectl", "get", "svc", "binder", "-n", "hub23", "|", "awk",
        "'{ print $4}'", "|", "tail", "-n", "1"
    ]).decode
    print(f"Binder IP (binder.hub23.turing.ac.uk): {output}")

if __name__ == "__main__":
    main()
