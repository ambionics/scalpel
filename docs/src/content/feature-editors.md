---
title: "Custom Burp editors"
menu: "features"
menu:
    features:
        weight: 2
---

# Custom Burp Editors

Scalpel's main _killer feature_ is the ability to **program your own editors** using Python.

## Table of content

-   [Event hooks](#event-hooks)
    1. [Edit a request](#1-edit-a-request)
    2. [Edit a response](#1-edit-a-response)
    3. [Multiple tabs example](#3-multiple-tabs-example)
-   [Binary editors](#binary-editors)

## Event hooks

#### 1. Edit a request

_E.g: A simple script to edit a fully URL encoded query string parameter in a request:_

```python
from pyscalpel import Request
from pyscalpel.utils import urldecode, urlencode_all


# Hook to initialize the editor's content
def req_edit_in(req: Request) -> bytes | None:
    param = req.query.get("filename")
    if param is not None:
        return urldecode(param)

    # Do not modify the request
    return None

# Hook to update the request from the editor's modified content
def req_edit_out(req: Request, modified_content: bytes) -> Request:
    req.query["filename"] = urlencode_all(modified_content)
    return req
```

-   If you open a request with a `filename` query parameter, a `Scalpel` tab should appear in the editor like shown below: {{< figure src="/screenshots/urlencode.png" >}}
-   Once your [`req_edit_in()`]({{< relref "addons-api#req_edit_in" >}}) Python hook is invoked, the tab should contain the `filename` parameter's URL decoded content. {{< figure src="/screenshots/decoded.png" >}}
-   You can modify it to update the request and thus, include anything you want (e.g: path traversal sequences). {{< figure src="/screenshots/traversal.png" >}}
-   When you send the request or switch to another editor tab, your Python hook [`req_edit_out()`]({{< relref "addons-api#req_edit_out" >}}) will be invoked to update the parameter. {{< figure src="/screenshots/updated.png" >}}


#### 2. Edit a response

It is the same process for editing responses:
```py
def res_edit_in(res: Response) -> bytes | None:
    # Displays an additional header in the editor
    res.headers["X-Python-In-Response-Editor"] = "res_edit_in"
    return bytes(res)


def res_edit_out(_: Response, text: bytes) -> Response | None:
    # Recreate a response from the editor's content
    res = Response.from_raw(text)
    return res
```

<br>

#### 3. Multiple tabs example

You can have multiple tabs open at the same time. Just **suffix** your function names:

_E.g: Same script as above but for two parameters: "filename" and "directory"._

```python
from pyscalpel import Request
from pyscalpel.utils import urldecode, urlencode_all

def req_edit_in_filename(req: Request):
    param = req.query.get("filename")
    if param is not None:
        return urldecode(param)

def req_edit_out_filename(req: Request, text: bytes):
    req.query["filename"] = urlencode_all(text)
    return req


def req_edit_in_directory(req: Request):
    param = req.query.get("directory")
    if param is not None:
        return urldecode(param)


def req_edit_out_directory(req: Request, text: bytes):
    req.query["directory"] = urlencode_all(text)
    return req
```

This will result in two open tabs. One for the `filename` parameter and one for the `directory` parameter (see the second image below).
{{< figure src="/screenshots/multiple_params.png" >}}
{{< figure src="/screenshots/multiple_tabs.png" >}}

<br>

## Binary editors

{{< readfile file="/generated/api/editors.html" >}}


### Example
_E.g.:  A simple script displaying requests in a hexadecimal editor and responses in a binary editor:_
```py
from pyscalpel import Request, Response, editor


@editor("hex")
def req_edit_in(req: Request) -> bytes | None:
    return bytes(req)

@editor("binary")
def res_edit_in(res: Response) -> bytes | None:
    return bytes(res)
```
_The hexadecimal editor:_
{{< figure src="/screenshots/bin-request.png" >}}

_The binary editor:_
{{< figure src="/screenshots/bin-response.png" >}}

<br>

## Further reading

Learn more about the available hooks in the technical documentation's [Event Hooks & API]({{< relref "addons-api" >}}) section.
