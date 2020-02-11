import sys
import argparse

from .hub import Hub

DESCRIPTION = "Manage a BinderHub deployment from the command line"
parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument(
    "action",
    choices=["generate-config-files", "get-logs", "helm-upgrade"],
    type=str,
    help="The management action to run on the BinderHub",
)
parser.add_argument(
    "--identity",
    action="store_true",
    help="Login to Azure with a Managed System Identity",
)
parser.add_argument(
    "--verbose", "-v", action="store_true", help="Turn on logging output"
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Perform a dry run of the helm upgrade",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debugging output for the helm upgrade",
)


def main():
    """Main function"""
    args = parser.parse_args(sys.argv[1:])
    obj = Hub(vars(args))

    if args.action == "generate-config-files":
        obj.generate_config_files()
    elif args.action == "get-logs":
        obj.get_logs()
    elif args.action == "helm-upgrade":
        obj.helm_upgrade()


if __name__ == "__main__":
    main()
