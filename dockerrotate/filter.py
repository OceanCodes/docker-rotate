import re


def include_tag(tag, patterns):
    """
    Return truthy if image tag should be considered for removal.
    """
    if not patterns:
        return True

    return all(regex_match(pattern, tag) for pattern in patterns)


def regex_match(pattern, tag):
    """
    Perform a regex match on the tag.
    """
    if pattern[0] == '~':
        return not re.search(pattern[1:], tag)
    return re.search(pattern, tag)
