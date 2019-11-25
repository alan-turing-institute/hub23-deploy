"""
Lints and validates the chart's template files and their rendered output without
any cluster interaction. For this script to function, you must install yamllint
and kubeval.

- https://github.com/adrienverge/yamllint

pip install yamllint

- https://github.com/garethr/kubeval

LATEST=curl --silent "https://api.github.com/repos/garethr/kubeval/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/'
wget https://github.com/garethr/kubeval/releases/download/$LATEST/kubeval-linux-amd64.tar.gz
tar xf kubeval-darwin-amd64.tar.gz
mv kubeval /usr/local/bin
"""

import os
import sys
import glob
import pipes
import argparse
import subprocess

# Change to Working Directory
os.chdir(os.path.dirname(sys.argv[0]))


def check_call(cmd, **kwargs):
    """Run a subcommand and exit if it fails"""
    try:
        subprocess.check_call(cmd, **kwargs)
    except subprocess.CalledProcessError as e:
        print(
            f"`{' '.join(map(pipes.quote, cmd))}` exited with status {e.returncode}",
            file=sys.stderr,
        )
        sys.exit(e.returncode)


def parse_args():
    """Argument Parser"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run helm lint and helm template with the --debug flag",
    )
    parser.add_argument(
        "--values",
        default="lint-and-validate-values.yaml",
        help="Specify helm values in a YAML file (can specify multiple)",
    )
    parser.add_argument(
        "-k",
        "--kubernetes-version",
        default="1.14.6",
        help="Version of Kubernetes to validate against",
    )
    parser.add_argument(
        "--output-dir",
        default="rendered-templates",
        help="Output directory for the rendered templates. Warning: Contents will be wiped.",
    )
    parser.add_argument(
        "--yamllint-config",
        default="yamllint-config.yaml",
        help="Specify a yamllint config",
    )

    return parser.parse_args()
