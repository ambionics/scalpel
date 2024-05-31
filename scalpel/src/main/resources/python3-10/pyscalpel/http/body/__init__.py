"""
    Pentesters often have to manipulate form data in precise and extensive ways

    This module contains implementations for the most common forms (multipart,urlencoded, JSON)
    
    Users may be implement their own form by creating a Serializer,
    assigning the .serializer attribute in `Request` and using the "form" property
    
    Forms are designed to be convertible from one to another.
    
    For example, JSON forms may be converted to URL encoded forms
    by using the php query string syntax:
    
    ```{"key1": {"key2" : {"key3" : "nested_value"}}} -> key1[key2][key3]=nested_value```
    
    And vice-versa.
"""

from .form import *


__all__ = [
    "Form",
    "JSON_VALUE_TYPES",
    "JSONForm",
    "MultiPartForm",
    "MultiPartFormField",
    "URLEncodedForm",
    "FormSerializer",
    "json_unescape",
    "json_unescape_bytes",
    "json_escape_bytes",
]
