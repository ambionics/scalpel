#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path
import sys
import os
import pdoc

parser = argparse.ArgumentParser(description="Build documentation.")
parser.add_argument(
    "--no-javadoc", action="store_true", help="Disable Javadoc generation"
)

args = parser.parse_args()

here = Path(__file__).parent
pyscalpel_path = here.parent / "scalpel" / "src" / "main" / "resources" / "python3-10"

os.environ["_DO_NOT_IMPORT_JAVA"] = "1"
os.environ["PYTHONPATH"] = f"{os.environ.get('PYTHONPATH') or ''}:{pyscalpel_path}"
sys.path.append(str(pyscalpel_path))

for script in sorted((here / "scripts").glob("*.py")):
    print(f"Generating output for {script.name}...")
    out = subprocess.check_output(
        ["python3", script.absolute()], cwd=here, text=True, env=os.environ
    )
    if out:
        (here / "src" / "generated" / f"{script.stem}.html").write_text(
            out, encoding="utf8"
        )

if (here / "public").exists():
    shutil.rmtree(here / "public")


subprocess.run(["hugo"], cwd=here / "src", check=True)
if not args.no_javadoc:
    subprocess.run(["./gradlew", "javadoc"], cwd=here.parent, check=True)
    shutil.copytree(
        here.parent / "scalpel" / "build" / "docs" / "javadoc",
        here / "public" / "javadoc",
        dirs_exist_ok=True,
    )

pdoc.pdoc(
    pyscalpel_path,
    output_directory=here / "public" / "pdoc",
)
