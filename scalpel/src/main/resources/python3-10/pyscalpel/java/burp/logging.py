# pylint: disable=invalid-name

from abc import abstractmethod
from pyscalpel.java.object import JavaObject

#
#   * Provides access to the functionality related to logging and events.
#


class Logging(JavaObject):  # pragma: no cover
    """generated source for interface Logging"""

    #
    #       * Obtain the current extension's standard output
    #       * stream. Extensions should write all output to this stream, allowing the
    #       * Burp user to configure how that output is handled from within the UI.
    #       *
    #       * @return The extension's standard output stream.
    #
    @abstractmethod
    def output(self) -> JavaObject:
        """generated source for method output"""

    #
    #       * Obtain the current extension's standard error
    #       * stream. Extensions should write all error messages to this stream,
    #       * allowing the Burp user to configure how that output is handled from
    #       * within the UI.
    #       *
    #       * @return The extension's standard error stream.
    #
    @abstractmethod
    def error(self) -> JavaObject:
        """generated source for method error"""

    #
    #       * This method prints a line of output to the current extension's standard
    #       * output stream.
    #       *
    #       * @param message The message to print.
    #
    @abstractmethod
    def logToOutput(self, message: str) -> None:
        """generated source for method logToOutput"""

    #
    #       * This method prints a line of output to the current extension's standard
    #       * error stream.
    #       *
    #       * @param message The message to print.
    #
    @abstractmethod
    def error(self, message: str) -> None:
        """generated source for method error"""

    #
    #       * This method can be used to display a debug event in the Burp Suite
    #       * event log.
    #       *
    #       * @param message The debug message to display.
    #
    @abstractmethod
    def raiseDebugEvent(self, message: str) -> None:
        """generated source for method raiseDebugEvent"""

    #
    #       * This method can be used to display an informational event in the Burp
    #       * Suite event log.
    #       *
    #       * @param message The informational message to display.
    #
    @abstractmethod
    def raiseInfoEvent(self, message: str) -> None:
        """generated source for method raiseInfoEvent"""

    #
    #       * This method can be used to display an error event in the Burp Suite
    #       * event log.
    #       *
    #       * @param message The error message to display.
    #
    @abstractmethod
    def raiseErrorEvent(self, message: str) -> None:
        """generated source for method raiseErrorEvent"""

    #
    #       * This method can be used to display a critical event in the Burp Suite
    #       * event log.
    #       *
    #       * @param message The critical message to display.
    #
    @abstractmethod
    def raiseCriticalEvent(self, message: str) -> None:
        """generated source for method raiseCriticalEvent"""
