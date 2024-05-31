from typing import TypedDict
from typing import Any


class Context(TypedDict):
    """Scalpel Python execution context"""

    API: Any
    """
        The Burp [Montoya API]
        (https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/MontoyaApi.html)
        root object.

        Allows you to interact with Burp by directly manipulating the Java object.
    
    """

    directory: str
    """The framework directory"""

    user_script: str
    """The loaded script path"""

    framework: str
    """The framework (loader script) path"""

    venv: str
    """The venv the script was loaded in"""
