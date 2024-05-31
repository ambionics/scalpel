"""
    To display the contents of your tab in a hexadecimal, binary, octal or decimal editor,
    the user can apply the `editor` decorator to the `req_edit_in` / `res_edit_in` hook:
"""
from pyscalpel.edit import editor


__all__ = ["editor"]
