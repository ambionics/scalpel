import re
from urllib.parse import quote_plus, unquote_plus
from typing import Mapping, Sequence, Any, cast
from copy import deepcopy

# NOTE: In this code "name" corresponds to an urlencoded key and "value" to an urlencoded value
#       "key" refers to the keys in a php style query name, and "field" refers to the base key in a php style query name
#       Example: "<field1>[<key1>][<key2>]=<value>&<field2>=<value>"


def list_to_dict(lst: list[Any]) -> dict[int, Any]:
    """Maps a list to an equivalent dictionary

    e.g: ["a","b","c"] -> {0:"a",1:"b",2:"c"}

    Used to convert lists to PHP-style arrays

    Args:
        lst (list[Any]): The list to transform

    Returns:
        dict[int, Any]: The "PHP-style array" dict
    """

    return {i: value for i, value in enumerate(lst)}


def is_valid_php_query_name(name: str) -> bool:
    """
    Check if a given name follows PHP query string syntax.
    This implementation assumes that names will be structured like:
    field
    field[key]
    field[key1][key2]
    field[]
    """
    pattern = r"""
    ^               # Asserts the start of the line, it means to start matching from the beginning of the string.
    [^\[\]&]+       # Matches one or more characters that are not `[`, `]`, or `&`. It describes the base key.
    (               # Opens a group. This group is used to match any subsequent keys within brackets.
    \[              # Matches a literal `[`, which is the start of a key.
    [^\[\]&]*       # Matches zero or more characters that are not `[`, `]`, or `&`, which is the content of a key.
    \]              # Matches a literal `]`, which is the end of a key.
    )*              # Closes the group and asserts that the group can appear zero or more times, for nested keys.
    $               # Asserts the end of the line, meaning the string should end with the preceding group.
    """
    return bool(re.match(pattern, name, re.VERBOSE))


def _get_name_value(tokens: dict, name: str, value: str, urlencoded: bool) -> None:
    """
    Parses the query string, and store the key/value pairs in the `tokens` dict.
    If the name doesn't follow PHP query string syntax, it treats it as a single key.

    Args:
        tokens (dict): The dictionary to store the parsed key/value pairs.
        name (str): The key from the query string.
        value (str): The value from the query string.
        urlencoded (bool): If True, decode the name and value.
    """
    if urlencoded:
        name = unquote_plus(name)
        value = unquote_plus(value)

    # If name doesn't follow PHP query string syntax, treat it as a single key
    if not is_valid_php_query_name(name):
        tokens[name] = value
        return

    pattern = r"""
    (              # Group start
        [^\[\]&]+  # One or more of any character except square brackets and the ampersand
        |          # Or
        \[\]       # Match empty square brackets
        |          # Or
        \[         # Match an opening square bracket
        [^\[\]&]*  # Zero or more of any character except square brackets and the ampersand
        \]         # Match a closing square bracket
    )              # Group end
    """
    matches = re.findall(pattern, name, re.VERBOSE)

    new_value: str | list | dict = value
    for i, match in enumerate(reversed(matches)):
        match match:
            case "[]":
                if i == 0:
                    new_value = [new_value]
                else:
                    new_value += new_value  # type: ignore

            # Regex pattern matches a string enclosed by square brackets. The string
            # may contain any character except square brackets and ampersand.
            case _ if re.match(r"\[[^\[\]&]*\]", match):
                # Here we're using another regular expression to remove the square
                # brackets from the match, thereby extracting the name.
                name = re.sub(r"[\[\]]", "", match)
                new_value = {name: new_value}

            case _:  # Plain field (no square brackets)
                if match not in tokens:
                    match new_value:
                        case list() | tuple():
                            tokens[match] = []
                        case dict():
                            tokens[match] = {}

                match new_value:
                    case _ if i == 0:
                        tokens[match] = new_value
                    case dict():
                        if isinstance(tokens[match], str):
                            tokens[match] = [tokens[match]]
                        tokens[match] = merge(new_value, tokens[match])
                    case list() | tuple():
                        tokens[match] = tokens[match] + list(new_value)
                    case _:
                        if not isinstance(tokens[match], list):
                            # The key is duplicated, so we transform the first value into a list so we can append the new one
                            tokens[match] = [tokens[match]]
                        tokens[match].append(new_value)


def merge_dict_in_list(source: dict, destination: list) -> list | dict:
    """
    Merge a dictionary into a list.

    Only the values of integer keys from the dictionary are merged into the list.

    If the dictionary contains only integer keys, returns a merged list.
    If the dictionary contains other keys as well, returns a merged dict.

    Args:
        source (dict): The dictionary to merge.
        destination (list): The list to merge.

    Returns:
        list | dict: Merged data.
    """
    # Retain only integer keys:
    int_keys = sorted([key for key in source.keys() if isinstance(key, int)])
    array_values = [source[key] for key in int_keys]
    merged_array = array_values + destination

    if len(int_keys) == len(source.keys()):
        return merged_array

    return merge(source, list_to_dict(merged_array))


def merge(source: dict | list, destination: dict | list, shallow: bool = True):
    """
    Merge the `source` and `destination`.
    Performs a shallow or deep merge based on the `shallow` flag.
    Args:
        source (Any): The source data to merge.
        destination (Any): The destination data to merge into.
        shallow (bool): If True, perform a shallow merge. Defaults to True.
    Returns:
        Any: Merged data.
    """
    if not shallow:
        source = deepcopy(source)
        destination = deepcopy(destination)

    match (source, destination):
        case (list(), list()):
            return source + destination
        case (dict(), list()):
            return merge_dict_in_list(source, destination)

    items = cast(Mapping, source).items()
    for key, value in items:
        if isinstance(value, dict) and isinstance(destination, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            node = merge(value, node)
            destination[key] = node
        else:
            if (
                isinstance(value, list) or isinstance(value, tuple)
            ) and key in destination:
                value = merge(destination[key], list(value))

            if isinstance(key, str) and isinstance(destination, list):
                destination = list_to_dict(
                    destination
                )  # << WRITE TEST THAT WILL REACH THIS LINE

            cast(dict, destination)[key] = value
    return destination


def qs_parse(
    qs: str, keep_blank_values: bool = True, strict_parsing: bool = False
) -> dict:
    """
    Parses a query string using PHP's nesting syntax, and returns a dict.

    Args:
        qs (str): The query string to parse.
        keep_blank_values (bool): If True, includes keys with blank values. Defaults to True.
        strict_parsing (bool): If True, raises ValueError on any errors. Defaults to False.

    Returns:
        dict: A dictionary representing the parsed query string.
    """

    tokens = {}
    pairs = [
        pair for query_segment in qs.split("&") for pair in query_segment.split(";")
    ]

    for name_val in pairs:
        if not name_val and not strict_parsing:
            continue
        nv = name_val.split("=")

        if len(nv) != 2:
            if strict_parsing:
                raise ValueError(f"Bad query field: {name_val}")
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append("")
            else:
                continue

        if len(nv[1]) or keep_blank_values:
            _get_name_value(tokens, nv[0], nv[1], urlencoded=True)

    return tokens


def build_qs(query: Mapping) -> str:
    """
    Build a query string from a dictionary or list of 2-tuples.
    Coerces data types before serialization.
    Args:
        query (Mapping): The query data to build the string from.
    Returns:
        str: A query string.
    """

    def dict_generator(indict, pre=None):
        pre = pre[:] if pre else []
        if isinstance(indict, dict):
            for key, value in indict.items():
                if isinstance(value, dict):
                    for d in dict_generator(value, pre + [key]):
                        yield d
                else:
                    yield pre + [key, value]
        else:
            yield indict

    paths = [i for i in dict_generator(query)]
    qs = []

    for path in paths:
        names = path[:-1]
        value = path[-1]
        s: list[str] = []
        for i, n in enumerate(names):
            n = f"[{n}]" if i > 0 else str(n)
            s.append(n)

        match value:
            case list() | tuple():
                for v in value:
                    multi = s[:]
                    if not s[-1].endswith("[]"):
                        multi.append("[]")
                    multi.append("=")
                    # URLEncode value
                    multi.append(quote_plus(str(v)))
                    qs.append("".join(multi))
            case _:
                s.append("=")
                # URLEncode value
                s.append(quote_plus(str(value)))
                qs.append("".join(s))

    return "&".join(qs)


def qs_parse_pairs(
    pairs: Sequence[tuple[str, str] | tuple[str]],
    keep_blank_values: bool = True,
    strict_parsing: bool = False,
) -> dict:
    """
    Parses a list of key/value pairs and returns a dict.

    Args:
        pairs (list[tuple[str, str]]): The list of key/value pairs.
        keep_blank_values (bool): If True, includes keys with blank values. Defaults to True.
        strict_parsing (bool): If True, raises ValueError on any errors. Defaults to False.

    Returns:
        dict: A dictionary representing the parsed pairs.
    """

    tokens = {}

    for name_val in pairs:
        if not name_val and not strict_parsing:
            continue
        nv = name_val

        if len(nv) != 2:
            if strict_parsing:
                raise ValueError(f"Bad query field: {name_val}")
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv = (nv[0], "")
            else:
                continue

        if len(nv[1]) or keep_blank_values:
            _get_name_value(tokens, nv[0], nv[1], False)

    return tokens
