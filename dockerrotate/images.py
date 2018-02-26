from collections import defaultdict

from docker.errors import APIError

from dockerrotate.filter import include_tag


def clean_images(args):
    """
    Delete old images keeping the most recent N images by tag.
    """
    # should not need to inspect all images; untagged parents should be deleted
    # along with dependent images
    images_by_name = defaultdict(list)
    for image in args.client.images.list(all=False):
        for tag in image.tags:
            if include_tag(tag, args.images):
                image_name = normalize_tag_name(tag)
                images_by_name[image_name].append((tag, image))

    for image_name, tags in images_by_name.items():
        # sort/keep
        tags_to_delete = sorted(
            tags,
            key=lambda tag: tag[1].attrs["Created"],
            reverse=True,
        )[args.keep:]

        # delete
        for tag in tags_to_delete:
            print "Removing image tag {}, ID: {}".format(
                tag[0],
                tag[1].id,
            )

            if args.dry_run:
                continue

            try:
                args.client.images.remove(tag[0])
            except APIError as ex:
                error = str(ex)
                # ignore failure to remove image as a result of a running container
                if ('running container' not in error and
                        'is using its referenced image' not in error):
                    print error


def normalize_tag_name(tag):
    """
    docker-py provides image names with tags as a single string.

    We want:

       some.domain.com/organization/image:tag -> organization/image
                       organization/image:tag -> organization/image
                                    image:tag ->              image
    """
    return "/".join(tag.rsplit(":", 1)[0].split("/")[-2:])
