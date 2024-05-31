---
title: "Installation"
menu: "overview"
menu:
    overview:
        weight: 2
---

# Installation

## Requirements

-   OpenJDK >= `17`
-   Python >= `3.8`
-   pip
-   python-virtualenv

### Debian-based distributions

The following packages are required:

```sh
sudo apt install build-essential python3 python3-dev python3-venv openjdk-17-jdk
```

### Fedora / RHEL / CentOS

The following packages are required:

```sh
sudo dnf install @development-tools python3 python3-devel python3-virtualenv java-17-openjdk-devel
```

### Arch-based distributions

The following packages are required:

```sh
sudo pacman -S base-devel python python-pip python-virtualenv jdk-openjdk
```

### Windows

Microsoft Visual C++ >=14.0 is required:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

## Step-by-step instructions

1.  Download the latest [JAR release](https://github.com/ambionics/scalpel/releases).
    {{< figure src="/screenshots/release.png" >}}

2.  Import the `.jar` to Burp.
    {{< figure src="/screenshots/import.png" >}}

3.  Wait for the dependencies to install.
    {{< figure src="/screenshots/wait.png" >}}

4.  Once Scalpel is properly initialized, you should get the following.
    {{< figure src="/screenshots/init.png" >}}

5.  If the installation was successful, a `Scalpel` tab should show in the Request/Response editor as follows:
    {{< figure src="/screenshots/tabs.png" >}}

6.  And also a `Scalpel` tab for configuration to install additional packages via terminal.
    {{< figure src="/screenshots/terminal.png" >}}

Scalpel is now properly installed and initialized!

> ### 💡 To unload and reload Scalpel, you must restart Burp, simply disabling and re-enabling the extension will **not** work

## What's next

-   Check the [Usage]({{< relref "overview-usage" >}}) page to get a glimpse of how to use the tool.
-   Read this [tutorial]({{< relref "tute-aes" >}}) to see Scalpel in a real use case context.
