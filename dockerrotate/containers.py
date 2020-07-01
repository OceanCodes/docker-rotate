from datetime import datetime, timedelta
from dateutil import parser
from dateutil.tz import tzutc
import re

from docker.errors import APIError


TIME_REGEX = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')  # noqa


def parse_time(time_str):
    """
    Parse a human readable time delta string.
    """
    parts = TIME_REGEX.match(time_str)
    if not parts:
        raise Exception("Invalid time delta format '{}'".format(time_str))
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def include_container(container, args):
    """
    Return truthy if container should be removed.
    """
    try:
        attrs = args.client.containers.get(container.id).attrs
    except:
        return False

    status = attrs["State"]["Status"]

    if status == "exited":
        finished_at = parser.parse(attrs["State"]["FinishedAt"])
        if (args.now - finished_at) < args.exited_ts:
            return False
    elif status == "created":
        created_at = parser.parse(attrs["Created"])
        if (args.now - created_at) < args.created_ts:
            return False
    elif status == "dead":
        finished_at = parser.parse(attrs["State"]["FinishedAt"])
        if (args.now - finished_at) < args.dead:
            return False
    else:
        return False

    return True


def clean_containers(args):
    """
    Delete non-running containers.

    Images cannot be deleted if in use. Deleting dead containers allows
    more images to be cleaned.
    """
    args.exited_ts = parse_time(args.exited)
    args.created_ts = parse_time(args.created)
    args.dead_ts = parse_time(args.dead)
    args.now = datetime.now(tzutc())

    containers = [
        container for container in args.client.containers.list(all=True)
        if include_container(container, args)
    ]

    for container in containers:
        try:
            image = container.image
        except:
            image = 'N/A'

        print "Removing container ID: {}, Name: {}, Image: {}".format(
            container.id,
            container.name,
            image,
        )

        if args.dry_run:
            continue

        try:
            container.remove()
        except APIError as error:
            print "Unable to remove container: {}: {}".format(
                container.id,
                error,
            )
