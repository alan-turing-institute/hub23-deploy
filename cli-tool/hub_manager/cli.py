import sys
import argparse

from .hub_manager import HubManager

DESCRIPTION = "Manage a BinderHub deployment from the command line"
parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument(
    "action",
    choices=[
        "generate-config-files",
        "get-logs",
        "helm-upgrade",
        "print-pods",
    ],
    type=str,
    help="The management action to run on the BinderHub",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Turn on logging output"
)
parser.add_argument(
    "--identity",
    action="store_true",
    help="Login to Azure with a Managed System Identity",
)
parser.add_argument(
    "--pod",
    type=str,
    default="jupyterhub",
    choices=["jupyterhub", "binder"],
    help="Define which pod to pull the logs for",
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
    obj = HubManager(vars(args))

    if args.action != "helm-upgrade":
        if args.dry_run:
            raise Exception(
                "--dry-run flag can only be used with helm-upgrade action"
            )
        elif args.debug:
            raise Exception(
                "--debug flag can only be used with helm-upgrade action"
            )
        elif args.dry_run and args.debug:
            raise Exception(
                "--dry-run and --debug flags can only be used with helm-upgrade action"
            )

    if args.action == "generate-config-files":
        obj.generate_config_files()
    elif args.action == "get-logs":
        obj.get_logs()
    elif args.action == "helm-upgrade":
        obj.helm_upgrade()
    elif args.action == "print-pods":
        obj.print_pods()


if __name__ == "__main__":
    main()
