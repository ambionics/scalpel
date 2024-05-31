---
title: "First steps"
menu:
    tutes:
        weight: 1
---

<!-- {{< figure src="/screenshots/traversal.png" >}} -->

# First Steps with Scalpel

## Introduction

Welcome to your first steps with Scalpel! This beginner-friendly tutorial will walk you through basic steps to automatically and interactively modify HTTP headers using Scalpel. By the end of this tutorial, you’ll be able to edit the content of the `User-Agent` and `Accept-Language` headers using Scalpel’s hooks and custom editors.

## Table of content

1. [Setting up Scalpel](#1-setting-up-scalpel)
2. [Inspecting a GET request](#2-inspecting-a-get-request)
3. [Create a new script](#3-creating-a-new-script)
4. [Manipulating headers](#4-manipulating-headers)
5. [Creating custom editors](#5-creating-custom-editors)
6. [Conclusion](#conclusion)

## 1. Setting up Scalpel

Before diving in, ensure Scalpel is [installed]({{< relref "overview-installation" >}}). Once done, you should have a `Scalpel` tab within Burp Suite.
{{< figure src="/screenshots/first-steps-0.png" >}}

## 2. Inspecting a GET request

Let’s start by inspecting a basic GET request. Open [https://httpbin.org/get](https://httpbin.org/get) in your Burp suite’s browser. This site simply returns details of the requests it receives, making it perfect for this example case.

Then, get back to Burp Suite. The GET request should show in your HTTP history.
{{< figure src="/screenshots/first-steps-1.png" >}}

Send it to Repeater using CTRL-R or right-click → `Send to Repeater`

## 3. Creating a new script

1. Select the `Scalpel` tab in the Burp GUI:
   {{< figure src="/screenshots/first-steps-2.png" >}}

2. Create a new script using the dedicated button:
   {{< figure src="/screenshots/first-steps-3.png" >}}
   ![alt text](error-popup.png)
3. Name it appropriately:
   {{< figure src="/screenshots/first-steps-4.png" >}}

4. Open the new script in a text editor:
   {{< figure src="/screenshots/first-steps-5.png" >}}
   {{< figure src="/screenshots/first-steps-6.png" >}}
    > 💡 The commands ran when selecting a script or opening it can be configured in the **_Settings_ tab**

## 4. Manipulating headers

This step will focus on manipulating the `User-Agent` header of the GET request.

With Scalpel, this header can easily be changed to a custom value. Here’s how:

```python
from pyscalpel import Request

def request(req: Request) -> Request:
	user_agent = req.headers.get("User-Agent")

	if user_agent:
	    req.headers["User-Agent"] = "My Custom User-Agent"

	return req
```

> 💡 The `request()` function modifies every requests going out of Burp.
>
> This includes the requests from the proxy (browser) and the repeater.

With the above code, every time you make a GET request, Scalpel will automatically change the `User-Agent` header to “My Custom User-Agent”.

To apply this effect:

1. Replace your script content with the snippet above.
2. Send the request to [https://httpbin.org/get](https://httpbin.org/get) using Repeater.
3. You should see in the response that your User-Agent header was indeed replaced by `My Custom User-Agent`.
   {{< figure src="/screenshots/first-steps-7.png" >}}

4. The process for modifying a response is the same. Add this to your script:

```python
from pyscalpel import Response

def response(res: Response) -> Response:
	date = res.headers.get("Date")

	if date:
		res.headers["Date"] = "My Custom Date"

	return res
```

5. The snippet above changed the `Date` header in response to `My Custom Date`. Send the request again and see the reflected changes:
   {{< figure src="/screenshots/first-steps-8.png" >}}

You now know how to programmatically edit HTTP requests and responses.

Next, let’s see how to interactively edit parts of a request.

## 5. Creating custom editors

Custom editors in Scalpel allow you to interactively change specific parts of a request. Let’s create an editor to change the `Accept-Language` header manually:

```python
def req_edit_in_accept_language(req: Request) -> bytes | None:
	return req.headers.get("Accept-Language", "").encode()

def req_edit_out_accept_language(req: Request, edited_text: bytes) -> Request:
	req.headers["Accept-Language"] = edited_text.decode()
	return req
```

Thanks to these hooks, when you open a GET request in Burp Suite, you’ll see an additional `Scalpel` tab. This tab enables you to edit the `Accept-Language` header’s content directly.
{{< figure src="/screenshots/first-steps-9.png" >}}

Once edited, Scalpel will replace the original `Accept-Language` value with your edited version.
{{< figure src="/screenshots/first-steps-10.png" >}}

## Conclusion

Congratulations! In this tutorial, you’ve taken your first steps with Scalpel. You’ve learned how to inspect GET requests, manipulate HTTP headers automatically, and create custom editors for interactive edits.

Remember, Scalpel is a powerful tool with a lot more capabilities. As you become more familiar with its features, you’ll discover its potential to significantly enhance your web security testing workflow.

---

# Further reading

Find **example use-cases [here]({{< relref "addons-examples" >}})**.

Read the [**technical documentation**](/pdoc/python/pyscalpel.html).

See an **advanced tutorial** for a real use case in [**Decrypting custom encryption**]({{< relref "tute-aes" >}}).
