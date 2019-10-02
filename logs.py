import argparse
from HubClass.Hub import Hub


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to print the JupyterHub logs to the terminal"
    )

    parser.add_argument(
        "-n", "--hub-name", type=str, default="hub23", help="BinderHub name"
    )
    parser.add_argument(
        "-c",
        "--cluster-name",
        type=str,
        default="hub23cluster",
        help="Azure Kubernetes cluster name",
    )
    parser.add_argument(
        "-g",
        "--resource_group",
        type=str,
        default="Hub23",
        help="Azure Resource Group",
    )
    parser.add_argument(
        "--identity",
        action="store_true",
        help="Login to Azure using a Managed System Identity",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    bot = Hub(vars(args))
    bot.get_logs()
