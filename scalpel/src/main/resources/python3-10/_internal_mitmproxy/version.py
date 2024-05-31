import os
import subprocess
import sys

VERSION = "8.0.0"
_internal_mitmproxy = "_internal_mitmproxy " + VERSION

# Serialization format version. This is displayed nowhere, it just needs to be incremented by one
# for each change in the file format.
FLOW_FORMAT_VERSION = 15


def get_dev_version() -> str:
    """
    Return a detailed version string, sourced either from VERSION or obtained dynamically using git.
    """

    _internal_mitmproxy_version = VERSION

    here = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        # Check that we're in the _internal_mitmproxy repository: https://github.com/_internal_mitmproxy/_internal_mitmproxy/issues/3987
        # cb0e3287090786fad566feb67ac07b8ef361b2c3 is the first _internal_mitmproxy commit.
        subprocess.run(
            ['git', 'cat-file', '-e', 'cb0e3287090786fad566feb67ac07b8ef361b2c3'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=here,
            check=True)
        git_describe = subprocess.check_output(
            ['git', 'describe', '--tags', '--long'],
            stderr=subprocess.STDOUT,
            cwd=here,
        )
        last_tag, tag_dist_str, commit = git_describe.decode().strip().rsplit("-", 2)
        commit = commit.lstrip("g")[:7]
        tag_dist = int(tag_dist_str)
    except Exception:
        pass
    else:
        # Add commit info for non-tagged releases
        if tag_dist > 0:
            _internal_mitmproxy_version += f" (+{tag_dist}, commit {commit})"

    # PyInstaller build indicator, if using precompiled binary
    if getattr(sys, 'frozen', False):
        _internal_mitmproxy_version += " binary"

    return _internal_mitmproxy_version


if __name__ == "__main__":  # pragma: no cover
    print(VERSION)
