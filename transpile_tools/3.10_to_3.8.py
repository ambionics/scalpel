import argparse
import os
import re
import sys
from pathlib import Path
from shutil import copy2
from transpiler import transform_to_legacy


def process_directory(
    input_dir: str, output_dir: str, exclude_patterns: list[str], verbose: bool
) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    compiled_excludes = [re.compile(pattern) for pattern in exclude_patterns]

    for current_dir, _, files in os.walk(input_path):
        for file in files:
            current_file_path = Path(current_dir) / file
            excluded = any(
                exclude.search(str(current_file_path)) for exclude in compiled_excludes
            )
            if not excluded and file.endswith(".py"):
                process_file(current_file_path, input_path, output_path, verbose)
            else:
                copy_non_python_file(
                    current_file_path, input_path, output_path, verbose
                )


def process_file(
    file_path: Path, input_base_path: Path, output_base_path: Path, verbose: bool
) -> None:
    relative_path = file_path.relative_to(input_base_path)
    output_file_path = output_base_path / relative_path

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "r") as file:
        code = file.read()

    new_code = transform_to_legacy(code)

    with open(output_file_path, "w") as file:
        file.write(new_code)

    if verbose:
        print(f"Processed {file_path} -> {output_file_path}")


def copy_non_python_file(
    file_path: Path, input_base_path: Path, output_base_path: Path, verbose: bool
) -> None:
    relative_path = file_path.relative_to(input_base_path)
    output_file_path = output_base_path / relative_path

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    copy2(file_path, output_file_path)

    if verbose:
        print(f"Copied {file_path} -> {output_file_path}")


def main():
    parser = argparse.ArgumentParser(description="Process a directory of files.")
    parser.add_argument("input_directory", type=str, help="Input directory path")
    parser.add_argument("output_directory", type=str, help="Output directory path")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Regex pattern to exclude files (can be used multiple times)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )

    args = parser.parse_args()

    process_directory(
        args.input_directory, args.output_directory, args.exclude, args.verbose
    )


if __name__ == "__main__":
    main()
