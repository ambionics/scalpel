---
title: "Intercept and rewrite HTTP traffic"
menu: "features"
menu:
    features:
        weight: 1
---

# Event Hooks

Scalpel scripts hook into Burps's internal mechanisms through [**event hooks**]({{< relref "addons-api" >}}).

These are implemented as methods with a set of well-known names.
Events receive [`Request`](../pdoc/python/pyscalpel.html#Request), [`Response`](../pdoc/python/pyscalpel.html#Response), [`Flow`](../pdoc/python/pyscalpel.html#Flow) and `bytes` objects as arguments. By modifying these objects, scripts can
change traffic on the fly and program custom request/response editors.

For instance, here is an script that adds a response
header with the number of seen responses:

```python
from pyscalpel import Response

count = 0

def response(res: Response) -> Response:
    global count

    count += 1
    res.headers["count"] = count
    return res
```

# Intercept and Rewrite HTTP Traffic

#### Request / Response

To intercept requests/responses, implement the [`request()`]({{< relref "addons-api#request" >}}) and [`response()`]({{< relref "addons-api#response" >}}) functions in your script:

_E.g: Hooks that add an arbitrary header to every request and response:_

```python
from pyscalpel import Request, Response

# Intercept the request
def request(req: Request) -> Request:
    # Add an header
    req.headers["X-Python-Intercept-Request"] = "request"
    # Return the modified request
    return req

# Same for response
def response(res: Response) -> Response:
    res.headers["X-Python-Intercept-Response"] = "response"
    return res
```

<br>

#### Match

Decide whether to intercept an HTTP message with the [`match()`]({{< relref "addons-api#match" >}}) function:

_E.g: A match intercepting requests to `localhost` and `127.0.0.1` only:_

```python
from pyscalpel import Flow

# If match() returns true, request(), response(), req_edit_in(), [...] callbacks will be used.
def match(flow: Flow) -> bool:
    # True if host is localhost or 127.0.0.1
    return flow.host_is("localhost", "127.0.0.1")
```

## Further reading

-   Learn more about the available hooks in the technical documentation's [Event Hooks & API]({{< relref "addons-api" >}}) section.
-   Or check out the [Custom Burp Editors]({{< relref "feature-editors" >}}).
