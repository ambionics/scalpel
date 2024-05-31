---
title: "Debugging"
menu: addons
weight: 3
---

# Debugging

Scalpel scripts can be **hard to debug**, as you cannot run them outside of Burp.

Also it is difficult to know if a bug is related to Scalpel/Burp context or to the user's implementation.

Here are a few advices for debugging Scalpel errors.

## Finding stacktraces

Errors that occur in scripts can be found in different places:

### 1. The **Output** tab

In the **Scalpel** tab, there is a sub-tab named **Script Output**, it shows all the standard output and error contents outputted by the current script
{{< figure src="/screenshots/output.png" >}}

### 2. The error popus

When an error happens in the hooks **request()** and **response()**, a popup is displayed.
{{< figure src="/screenshots/error-popup.png" >}}

This popup can be disabled in the Settings tab

### 3. The dashboard event log

{{< figure src="/screenshots/debug-image.png" >}}
The user may click on the events to get the full error message:
{{< figure src="/screenshots/debug-image-1.png" >}}

### 4. The extensions logs

{{< figure src="/screenshots/debug-image-2.png" >}}

### 5. The command line output **(best)**

{{< figure src="/screenshots/debug-image-3.png" >}}

> 💡 When debugging, it is best to launch Burp in CLI, as the CLI output will contain absolutely all errors and logs, which is not always the case in the Burp GUI (e.g: In case of deadlocks, crashes and other tricky issues).
