---
title: "How scalpel works"
menu:
    concepts:
        weight: 1
---

# How Scalpel works

## Table of content

- [Dependencies](#dependencies)
- [Behavior](#behavior)
- [Python scripting](#python-scripting)
- [Diagram](#diagram)

## Dependencies

-   Scalpel's Python library is embedded in a JAR file and is unzipped when Burp loads the extension.
-   Scalpel requires external dependencies and will install them using `pip` when needed.
-   Scalpel will always use a virtual environment for every action. Hence, it will never modify the user's global Python installation.
-   Scalpel relies on [Jep](https://github.com/ninia/jep/) to communicate with Python. It requires to have a JDK installed on your machine.
-   User scripts are executed in a virtual environment selected from the `Scalpel` tab.
-   Scalpel provides a terminal with a shell running in the selected virtual environment to easily install packages.
-   Creating new virtual environments or adding existing ones can be done via the dedicated GUI.
-   All data is stored in the `~/.scalpel` directory.

## Behavior

-   Scalpel uses the Java [Burp Montoya API](https://portswigger.net/burp/documentation/desktop/extensions) to interact with Burp.
-   Scalpel uses Java to handle the dependencies installation, HTTP and GUI for Burp, and communication with Python.
-   Scalpel uses [Jep](https://github.com/ninia/jep/) to execute Python from Java.
-   Python execution is handled through a task queue in a dedicated thread that will execute one Python task at a time in a thread-safe way.
-   All Python hooks are executed through a `_framework.py` file that will activate the selected venv, load the user script file, look for callable objects matching the hooks names (`match, request, response, req_edit_in, res_edit_in, req_edit_out, res_edit_out, req_edit_in_<tab_name>, res_edit_in_<tab_name>, req_edit_out_<tab_name>, res_edit_out_<tab_name>`).
-   The `_framework.py` declares callbacks that receive Java objects, convert them to custom easy-to-use Python objects, pass the Python objects to the corresponding user hook, get back the modified Python objects and convert them back to Java objects.
-   Java code receives the hook's result and interact with Burp to apply its effects.
-   At each task, Scalpel checks whether the user script file changed. If so, it reloads and restarts the interpreter.

## Python scripting

-   Scalpel uses a single shared interpreter. Then, if any global variables are changed in a hook, their values remain changed in the next hook calls.
-   For easy Python scripting, Scalpel provides many utilities described in the [Event Hooks & API]({{< relref "addons-api" >}}) section.

## Diagram

Here is a diagram illustating the points above:
{{< figure src="/schematics/scalpel-diagram.svg" >}}
