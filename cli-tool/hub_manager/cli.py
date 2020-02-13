import sys
import argparse

from .hub_manager import HubManager

DESCRIPTION = "Manage a BinderHub deployment from the command line"
parser = argparse.ArgumentParser(description=DESCRIPTION)
subparsers = parser.add_subparsers(
    help="hub-manager subcommands", dest="subcommand", required=True
)

# Define global option flags
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Turn on logging output"
)
parser.add_argument(
    "--identity",
    action="store_true",
    help="Login to Azure with a Managed System Identity",
)

# Add generate-config subcommand
generate_config = subparsers.add_parser(
    "generate-config", help="Generate the configuration files for Hub23"
)

# Add get-logs subcommand
get_logs = subparsers.add_parser(
    "get-logs", help="Pull the logs of a Kubernetes pod. Default: hub pod."
)
get_logs.add_argument(
    "--pod",
    choices=["hub", "binder"],
    default="hub",
    help="Define which Kubernetes pod to pull the logs for",
)

# Add helm-upgrade subcommand
helm_upgrade = subparsers.add_parser(
    "helm-upgrade", help="Perform an upgrade of the Hub23 helm chart"
)
helm_upgrade.add_argument(
    "--dry-run",
    action="store_true",
    help="Perform a dry run of the helm upgrade",
)
helm_upgrade.add_argument(
    "--debug",
    action="store_true",
    help="Enable debugging output for the helm upgrade",
)

# Add print-pods subcommand
print_pods = subparsers.add_parser(
    "print-pods", help="Print the status of the running Kubernetes pods"
)


def main():
    """Main function"""
    args = parser.parse_args(sys.argv[1:])
    print(vars(args))
    obj = HubManager(vars(args))

    if args.subcommand == "generate-config":
        obj.generate_config_files()
    elif args.subcommand == "get-logs":
        obj.get_logs()
    elif args.subcommand == "helm-upgrade":
        obj.helm_upgrade()
    elif args.subcommand == "print-pods":
        obj.print_pods()


if __name__ == "__main__":
    main()
