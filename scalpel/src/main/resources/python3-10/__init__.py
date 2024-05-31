"""
# Python libraries bundled with Scalpel

---

## [pyscalpel](python3-10/pyscalpel.html)
This is a module providing tools to handle Burp HTTP traffic through the use of the Scalpel extension.

It provides many utilities to manipulate HTTP requests, responses and converting data.

---

## [qs](python3-10/qs.html)
A small module to parse PHP-style query strings.

Used by pyscalpel

---

# [← Go back to the user documentation](../)
"""

import pyscalpel
import qs


__all__ = ["pyscalpel", "qs"]
