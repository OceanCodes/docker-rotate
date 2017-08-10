from collections import defaultdict

from docker.errors import APIError

from dockerrotate.filter import include_image


def clean_images(args):
    """
    Delete old images keeping the most recent N images by tag.
    """
    # should not need to inspect all images; only intermediate images should appear
    # when all is true; these should be deleted along with dependent images
    images = [image
              for image in args.client.images.list(all=False)
              if include_image(image.tags, args)]

    # index by id
    images_by_id = {
        image.id: image for image in images
    }

    # group by name
    images_by_name = defaultdict(set)
    for image in images:
        for tag in image.tags:
            image_name = normalize_tag_name(tag)
            images_by_name[image_name].add(image.id)

    for image_name, image_ids in images_by_name.items():
        # sort/keep
        images_to_delete = sorted([
            images_by_id[image_id] for image_id in image_ids],
            key=lambda image: -image.attrs["Created"],
        )[args.keep:]

        # delete
        for image in images_to_delete:
            print "Removing image ID: {}, Tags: {}".format(
                image.id,
                ", ".join(image.tags)
            )

            if args.dry_run:
                continue

            try:
                args.client.images.remove(image.id, force=True, noprune=False)
            except APIError as ex:
                error = str(ex)
                # ignore failure to remove image as a result of running container
                if 'running container' not in error:
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
