from fnmatch import fnmatch


def match_patterns(to_match: str, *patterns: str) -> bool:
    """Matches a string using unix-like wildcard matching against multiple patterns

    Args:
        to_match (str): The string to match against
        patterns (str): The patterns to use

    Returns:
        bool: The match result (True if at least one pattern matches, else False)
    """
    for pattern in patterns:
        if fnmatch(to_match, pattern):
            return True
    return False


def host_is(host: str, *patterns: str) -> bool:
    """Matches a host using unix-like wildcard matching against multiple patterns

    Args:
        host (str): The host to match against
        patterns (str): The patterns to use

    Returns:
        bool: The match result (True if at least one pattern matches, else False)
    """
    return match_patterns(host, *patterns)
