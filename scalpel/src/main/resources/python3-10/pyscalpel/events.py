"""Events that can be passed to the match() hook"""

from typing import Literal, get_args

MatchEvent = Literal[
    "request",
    "response",
    "req_edit_in",
    "req_edit_out",
    "res_edit_in",
    "res_edit_out",
]


MATCH_EVENTS: set[MatchEvent] = set(get_args(MatchEvent))
