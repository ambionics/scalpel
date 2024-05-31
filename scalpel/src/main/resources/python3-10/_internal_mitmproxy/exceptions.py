"""

Edit 2020-12 @mhils:
    The advice below hasn't paid off in any form. We now just use builtin exceptions and specialize where necessary.

---

We try to be very hygienic regarding the exceptions we throw:

- Every exception that might be externally visible to users shall be a subclass
  of _internal_mitmproxyException.p
- Every exception in the base net module shall be a subclass
  of NetlibException, and will not be propagated directly to users.

See also: http://lucumr.pocoo.org/2014/10/16/on-error-handling/
"""


class _internal_mitmproxyException(Exception):
    """
    Base class for all exceptions thrown by _internal_mitmproxy.
    """

    def __init__(self, message=None):
        super().__init__(message)


class FlowReadException(_internal_mitmproxyException):
    pass


class ControlException(_internal_mitmproxyException):
    pass


class CommandError(Exception):
    pass


class OptionsError(_internal_mitmproxyException):
    pass


class AddonManagerError(_internal_mitmproxyException):
    pass


class AddonHalt(_internal_mitmproxyException):
    """
        Raised by addons to signal that no further handlers should handle this event.
    """
    pass


class TypeError(_internal_mitmproxyException):
    pass
