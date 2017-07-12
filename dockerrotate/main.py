"""
Free up space by rotating out old Docker images and containers.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from docker import DockerClient
from docker.errors import NotFound

from dockerrotate.images import clean_images
from dockerrotate.containers import clean_containers


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove anything",
    )
    parser.add_argument(
        "--client-version",
        help="Specify client version to use.",
    )

    subparsers = parser.add_subparsers()

    images_parser = subparsers.add_parser(
        "images",
        help="Clean out old images",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    images_parser.set_defaults(cmd=clean_images)
    images_parser.add_argument(
        "--keep",
        "-k",
        type=int,
        default=3,
        help="Keep this many images of each kind",
    )
    images_parser.add_argument(
        "--images",
        nargs='*',
        help="Python regex of image names to remove. Use a '~' prefix for negative match.",
    )

    containers_parser = subparsers.add_parser(
        "containers",
        help="Clean out old containers",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    containers_parser.set_defaults(cmd=clean_containers)
    containers_parser.add_argument(
        "--exited",
        default="1h",
        help="Remove only containers that exited that long ago",
    )
    containers_parser.add_argument(
        "--created",
        default="1d",
        help="Remove only containers that where created (but not running) that long ago",
    )
    containers_parser.add_argument(
        "--dead",
        default="1m",
        help="Remove \"dead\" containers that finished at least this long ago",
    )

    return parser.parse_args()


def make_client(args):
    """
    Create a Docker client.
    """
    kwargs = {}

    if args.client_version:
        kwargs["version"] = args.client_version

    client = DockerClient.from_env(**kwargs)

    # Verify client can talk to server.
    try:
        client.version()
    except NotFound as error:
        raise SystemExit(error)

    return client


def main():
    """
    CLI entry point.
    """
    args = parse_args()
    args.client = make_client(args)

    args.cmd(args)
