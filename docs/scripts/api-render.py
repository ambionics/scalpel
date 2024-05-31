#!/usr/bin/env python3
import os
import shutil
import textwrap
from pathlib import Path

import pdoc.render_helpers

here = Path(__file__).parent

if os.environ.get("DOCS_ARCHIVE", False):
    edit_url_map = {}
else:
    edit_url_map = {
        "scalpel": "https://REMOVED/scalpel",
    }

pdoc.render.configure(
    template_directory=here / "pdoc-template",
    edit_url_map=edit_url_map,
)

# We can't configure Hugo, but we can configure pdoc.
pdoc.render_helpers.formatter.cssclass = "chroma pdoc-code"

modules = [
    "pyscalpel.http",
    "pyscalpel.http.body",
    "pyscalpel.edit",
    "pyscalpel.events",
    "pyscalpel.venv",
    "pyscalpel.utils",
    "pyscalpel.encoding",
    "pyscalpel.java",
    "pyscalpel.java.burp",
    here / ".." / "src" / "declarations" / "events.py",
    here / ".." / "src" / "declarations" / "editors.py",
]

pdoc.pdoc(*modules, output_directory=here / ".." / "src" / "generated" / "api")

api_content = here / ".." / "src" / "content" / "api"
if api_content.exists():
    shutil.rmtree(api_content)

api_content.mkdir()

for weight, module in enumerate(modules):
    if isinstance(module, Path):
        continue
    filename = f"api/{module.replace('.', '/')}.html"
    (api_content / f"{module}.md").write_bytes(
        textwrap.dedent(
            f"""
        ---
        title: "{module}"
        url: "{filename}"

        menu:
            addons:
                parent: 'Event Hooks & API'
                weight: {weight + 1}
        ---

        {{{{< readfile file="/generated/{filename}" >}}}}
        """
        ).encode()
    )

(here / ".." / "src" / "content" / "addons-api.md").touch()
