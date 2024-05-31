---
title: "Usage"
menu: "overview"
menu:
    overview:
        weight: 2
---

# Usage

Scalpel allows you to programmatically intercept and modify HTTP requests/responses going through Burp, as well as creating custom request/response editors with Python.

To do so, Scalpel provides a **Burp extension GUI** for scripting and a set of **predefined function names** corresponding to specific actions:

-   [`match`]({{< relref "addons-api#match" >}}): Determine whether an event should be handled by a hook.
-   [`request`]({{< relref "addons-api#request" >}}): Intercept and rewrite a request.
-   [`response`]({{< relref "addons-api#response" >}}): Intercept and rewrite a response.
-   [`req_edit_in`]({{< relref "addons-api#req_edit_in" >}}): Create or update a request editor's content from a request.
-   [`req_edit_out`]({{< relref "addons-api#req_edit_out" >}}): Update a request from an editor's modified content.
-   [`res_edit_in`]({{< relref "addons-api#res_edit_in" >}}): Create or update a response editor's content from a response.
-   [`res_edit_out`]({{< relref "addons-api#res_edit_out" >}}): Update a response from an editor's modified content.

Simply write a Python script implementing the ones you need and load the file with Scalpel Burp GUI: {{< figure src="/screenshots//choose_script.png" >}}
<!-- ^^ TODO: Better screenshot -->

>  ### 💡 To get started with Scalpel, see [First steps]({{< relref "tute-first-steps" >}})
## Further reading

Learn more about the predefined function names and find examples in the [Features]({{< relref "feature-http" >}}) category.
