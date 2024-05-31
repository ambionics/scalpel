---
title: "Event Hooks & API"
url: "api/events.html"
aliases:
    - /addons-events/
layout: single
menu:
    addons:
        weight: 1
---

## Available Hooks

The following list all available event hooks.

The full Python documentation is available **[here](../../pdoc/python3-10/pyscalpel.html)**

{{< readfile file="/generated/api/events.html" >}}

## ⚠️ Good to know

-   If your hooks return `None`, they will follow these behaviors:

    -   `request()` or `response()`: The original request is be **forwarded without any modifications**.
    -   `req_edit_in()` or `res_edit_in()`: The editor tab is **not displayed**.
    -   `req_edit_out()` or `res_edit_out()`: The request is **not modified**.

-   If `req_edit_out()` or `res_edit_out()` isn't declared but `req_edit_in()` or `res_edit_in()` is, the corresponding editor will be **read-only**.

-   You do not have to declare every hook if you don't need them, if you only want to modify requests, you can declare the `request()` hook only.

## Further reading

Check out the [Custom Burp Editors]({{< relref "feature-editors" >}}) section.
