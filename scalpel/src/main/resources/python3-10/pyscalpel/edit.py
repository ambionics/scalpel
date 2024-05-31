"""
    Scalpel allows choosing between normal and binary editors,
    to do so, the user can apply the `editor` decorator to the `req_edit_in` / `res_edit_int` hook:
"""
from typing import Callable, Literal, get_args

EditorMode = Literal["raw", "hex", "octal", "binary", "decimal"]
EDITOR_MODES: set[EditorMode] = set(get_args(EditorMode))


def editor(mode: EditorMode):
    """Decorator to specify the editor type for a given hook

    This can be applied to a req_edit_in / res_edit_in hook declaration to specify the editor that should be displayed in Burp

    Example:
    ```py
        @editor("hex")
        def req_edit_in(req: Request) -> bytes | None:
            return bytes(req)
    ```
    This displays the request in an hex editor.

    Currently, the only modes supported are `"raw"`, `"hex"`, `"octal"`, `"binary"` and `"decimal"`.


    Args:
        mode (EDITOR_MODE): The editor mode (raw, hex,...)
    """

    if mode not in EDITOR_MODES:
        raise ValueError(f"Argument must be one of {EDITOR_MODES}")

    def decorator(hook: Callable):
        hook.__annotations__["scalpel_editor_mode"] = mode
        return hook

    return decorator
