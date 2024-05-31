---
title: "Introduction"
layout: single
menu:
    overview:
        weight: 1
---

# Introduction

Scalpel is a powerful **Burp Suite** extension that allows you to script Burp in order to intercept, rewrite HTTP traffic on the fly, and program custom Burp editors in Python 3.

It provides an interactive way to edit encoded/encrypted data as plaintext and offers an easy-to-use Python library as an alternative to Burp's Java API.

# Index

-   [Installation]({{< relref "overview-installation" >}})
-   [Usage]({{< relref "overview-usage" >}})
-   [First steps]({{< relref "tute-first-steps" >}})
-   [FAQ]({{< relref "overview-faq" >}})
-   [Technical documentation for script development]({{< relref "addons-api" >}})
-   [Example use-case]({{< relref "tute-aes" >}})
-   [How scalpel works]({{< relref "concepts-howscalpelworks" >}})

## Features

-   [**Python Library**]({{< relref "addons-api" >}}): Easy-to-use Python library, especially welcome for non-Java developers.
-   [**Intercept and Rewrite HTTP Traffic**]({{< relref "feature-http"  >}}): Scalpel provides a set of predefined function names that can be implemented to intercept and modify HTTP requests and responses.
-   [**Custom Burp Editors**]({{< relref "feature-editors" >}}): Program your own Burp editors in Python. Encoded/encrypted data can be handled as plaintext.
    -   [**Hex Editors**]({{< relref "feature-editors#binary-editors" >}}): Ability to create improved hex editors.

## Use cases

-   [Decrypting custom encryption]({{< relref "tute-aes" >}})
-   [Editing encoded requests/responses]({{< relref "addons-examples#GZIP" >}})

> Note: One might think existing Burp extensions like `Piper` can handle such cases. But actually they can't.  
> For example, when intercepting a response, `Piper` cannot get information from the initiating request, which is required in the above use cases. Scalpel generally allows you to manage complex cases that are not handled by other Burp extensions like `Piper` or `Hackvertor`.
