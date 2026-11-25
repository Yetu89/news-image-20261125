"""Deliver the built front page to the harness output directory.

The picture itself is painted by tools/build_image.py and stored in
this repository as entry.png. This entrypoint only checks that file
and copies it to $OUTPUT_DIR/entry.png (or /output/entry.png when the
variable is unset). It uses the standard library alone, touches no
network, and writes the same bytes on every run.
"""

import hashlib
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PICTURE = os.path.join(BASE, "entry.png")
LIMIT = 1048576  # the gate refuses anything over 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    """Report a problem on stderr and return a failing exit code."""
    print(f"error: {message}", file=sys.stderr)
    return 1


def target_dir():
    """Where the harness wants the picture, honouring the env first."""
    wanted = os.environ.get("OUTPUT_DIR")
    if wanted:
        return wanted
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if wanted:
        return wanted
    return "/output"


def check_picture():
    """Confirm entry.png exists, is a PNG, and fits the size gate.

    Returns the file size in bytes, or -1 after reporting a problem.
    """
    if not os.path.isfile(PICTURE):
        fail("entry.png is missing next to main.py")
        return -1
    size = os.path.getsize(PICTURE)
    if size > LIMIT:
        fail(f"entry.png is {size} bytes, over the 1 MiB limit")
        return -1
    with open(PICTURE, "rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        fail("entry.png does not start with the PNG signature")
        return -1
    return size


def digest(path):
    """Hex SHA-256 of a file, read in blocks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    size = check_picture()
    if size < 0:
        return 1
    out_dir = target_dir()
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(PICTURE, dest)
    copied = os.path.getsize(dest)
    if copied != size:
        return fail(f"copied {copied} bytes but entry.png has {size}")
    if digest(dest) != digest(PICTURE):
        return fail("the copied file does not match entry.png")
    print(f"wrote {dest} ({copied} bytes, sha256 {digest(dest)[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
