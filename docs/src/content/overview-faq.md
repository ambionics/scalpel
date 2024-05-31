---
title: "FAQ"
menu: "overview"
menu:
    overview:
        weight: 3
---

# FAQ

## Table of Contents

1. [Why does Scalpel depend on JDK whereas Burp comes with its own JRE?](#why-does-scalpel-depend-on-jdk-whereas-burp-comes-with-its-own-jre)
2. [Why using Java with Jep to execute Python whereas Burp already supports Python extensions with Jython?](#why-using-java-with-jep-to-execute-python-whereas-burp-already-supports-python-extensions-with-jython)
3. [Once the .jar is loaded, no additional request shows up in the editor](#once-the-jar-is-loaded-no-additional-request-shows-up-in-the-editor)
4. [My distribution/OS comes with an outdated python.](#scalpel-requires-python-310-but-my-distribution-is-outdated-and-i-cant-install-such-recent-python-versions-using-the-package-manager)
5. [Configuring my editor for Python](#how-can-i-configure-my-editor-to-recognize-the-python-library)
6. [I installed Python using the Microsoft Store and Scalpel doesn't work.](#i-installed-python-using-the-microsoft-store-and-scalpel-doesnt-work)

---

### Why does Scalpel depend on JDK whereas Burp comes with its own JRE?

-   Scalpel uses a project called [`jep`](https://github.com/ninia/jep/wiki/) to call Python from Java. `jep` needs a JDK to function.
-   If you are curious or need more technical information about Scalpel's implementation, read [How scalpel works]({{< relref "concepts-howscalpelworks" >}}).

### Why using Java with Jep to execute Python whereas Burp already supports Python extensions with [Jython](https://www.jython.org/)?

-   Jython supports up to Python 2.7. Unfortunately, Python 3 is not handled at all. Python 2.7 is basically a dead language and nobody should still be using it.
-   Burp's developers released a [new API](https://portswigger.net/burp/documentation/desktop/extensions/creating) for extensions and deprecated the former one. The new version only supports Java. That's why the most appropriate choice was to reimplement a partial Python scripting support for Burp.

### Once the .jar is loaded, no additional request shows up in the editor!

-   When first installing Scalpel, the installation of all its dependencies may take a while. Look at the "Output" logs in the Burp "Extension" tab to ensure that the extension has completed.
-   Examine the "Errors" logs in the Burp "Extension" tab. There should be an explicit error message with some tips to solve the problem.
-   Make sure you followed the [installation guidelines](../install.md). In case you didn't, remove the `~/.scalpel` directory and try one more time.
-   If the error message doesn't help, please open a GitHub issue including the "Output" and "Errors" logs, and your system information (OS / Distribution version, CPU architecture, JDK and Python version and installation path, environment variables which Burp runs with, and so forth).

### Scalpel requires python >=3.8 but my distribution is outdated and I can't install such recent Python versions using the package manager.

-   Try updating your distribution.
-   If that is not possible, you must setup a separate Python >=3.8 installation and run Burp with the appropriate environment so this separate installation is used.
    > 💡 Tip: Use [`pyenv`](https://github.com/pyenv/pyenv) to easily install different Python versions and switch between them.

### How can I configure my editor to recognize the Python library

-   Python modules are extracted in `~/.scalpel/.extracted/python`, adding this to your PYTHONPATH should do it.
-   For **VSCode users**, Scalpel extracts a .vscode containing the correct settings in the scripts directory, so you can simply open the folder and it should work out of the box.

    -   Alternatively, you can use the following `settings.json`:

        ```JSON
        {
            "terminal.integrated.env.linux": {
                "PYTHONPATH": "${env:HOME}/.scalpel/extracted/python:${env:PYTHONPATH}",
                "PATH": "${env:HOME}/.scalpel/extracted/python:${env:PATH}"
            },

            // '~' or ${env:HOME} is not supported by this setting, it must be replaced manually.
            "python.analysis.extraPaths": ["<REPLACE_WITH_ABSOLUTE_HOME_PATH>/.extracted/python"]
        }
        ```

### I installed Python using the Microsoft Store and Scalpel doesn't work.

-   The Microsoft Store Python is a sandboxed version designed for educational purposes. Many of its behaviors are incompatible with Scalpel. To use Scalpel on Windows, it is required to install Python from the [official source](https://www.python.org/downloads/windows/).

### error: `command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1`

-   Some users encouter this error when the python developpement libraries are missing:

```
x86_64-linux-gnu-gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O2 -Wall -g -fstack-protector-strong -Wformat -Werror=format-security -g -fwrapv -O2 -fPIC -DPACKAGE=jep -DUSE_DEALLOC=1 -DJEP_NUMPY_ENABLED=0 -DVERSION=\"4.1.1\" -DPYTHON_LDLIBRARY=\"libpython3.10.so\" -I/usr/lib/jvm/java-11-openjdk-amd64/include -I/usr/lib/jvm/java-11-openjdk-amd64/include/linux -Isrc/main/c/Include -Ibuild/include -I/home/<user>/.scalpel/venvs/default/.venv/include -I/usr/include/python3.10 -c src/main/c/Jep/convert_j2p.c -o build/temp.linux-x86_64-cpython-310/src/main/c/Jep/convert_j2p.o
      In file included from src/main/c/Include/Jep.h:35,
                       from src/main/c/Jep/convert_j2p.c:28:
      src/main/c/Include/jep_platform.h:35:10: fatal error: Python.h: Aucun fichier ou dossier de ce type
         35 | #include <Python.h>
            |          ^~~~~~~~~~
      compilation terminated.
      error: command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1
      [end of output]
```

-   Make sure you installed the python3-dev libraries for your python version
    https://stackoverflow.com/a/57698471
