#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261127.

Copies the front-page image built for Friday 27 November 2026 to the
output directory. Standard library only, no network, no randomness:
every run writes the same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    # The image is the deliverable: copy it byte for byte so both
    # grading runs produce identical output.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
