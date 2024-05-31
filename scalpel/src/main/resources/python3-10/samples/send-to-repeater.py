"""
    Script for Automated Sending to Burp Repeater

    This script sends HTTP requests containing a specific parameter to the Repeater tool in Burp Suite. 
    The parameter it checks for is 'cmd', but this can be modified as needed. 
    The script also keeps track of previously seen 'cmd' values to avoid resending the same request.
"""

from pyscalpel import Request
from pyscalpel.burp import send_to_repeater

# A set is used to store the values of the 'cmd' parameter that have already been encountered.
# The use of a set ensures that each value is stored only once, avoiding duplicate requests being sent to Repeater.
seen = set()


def request(req: Request) -> None:
    """
    If the 'cmd' parameter is present in the request and its value hasn't been seen before, the request is sent to Repeater.

    Args:
        req: The incoming HTTP request.

    Returns:
        None
    """
    cmd = req.query.get("cmd")
    if cmd is not None and cmd not in seen:
        # If the 'cmd' parameter is present and its value is new, add the value to the 'seen' set.
        seen.add(cmd)

        # Send the request to Repeater with a caption indicating the value of the 'cmd' parameter.
        send_to_repeater(req, f"cmd={cmd}")
