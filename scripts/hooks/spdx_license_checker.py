import argparse
import re
from pathlib import Path
from typing import Tuple

from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound


def get_spdx_license_regex(file_path: Path, pattern: str) -> str:
    """Return a regex pattern to match SPDX license header."""
    spdx_matcher = (
        r"SPDX-License-Identifier:.*"
        if not pattern
        else rf"SPDX-License-Identifier:\s*{re.escape(pattern)}"
    )
    comment_prefix = get_comment_style(file_path)[0]
    comment_prefix = comment_prefix.split("\n")[-1]  # don't match across lines
    return f"{comment_prefix}\\s*{spdx_matcher}".replace("\n", ".")


def get_comment_style(file_path: Path) -> Tuple[str, str]:
    """Determine the comment style for a given file based on its type."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        lexer = guess_lexer_for_filename(file_path.name, content)
    except (OSError, UnicodeDecodeError, ClassNotFound):
        return "#", ""  # Default to hash-style comments

    # Return single-line comment style for the lexer
    if hasattr(lexer, "inline_comment_prefixes"):
        return lexer.inline_comment_prefixes[0], ""
    if file_path.suffix == ".md":
        return "<!--\n", "\n-->"
    return "#", ""


def add_spdx_header(file_path: Path, spdx_id: str) -> None:
    """Add SPDX license header to the file."""
    try:
        comment_prefix, comment_suffix = get_comment_style(file_path)
        spdx_header = f"{comment_prefix} SPDX-License-Identifier: {spdx_id}{comment_suffix}\n\n"

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.readlines()

        # Check if there's a shebang (e.g., #!/usr/bin/env python) and insert after it
        if content and content[0].startswith("#!"):
            content.insert(1, spdx_header)
        else:
            content.insert(0, spdx_header)

        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(content)

    except (OSError, UnicodeDecodeError):
        # Skip binary files or unreadable files
        pass


def check_spdx_header(file_path: Path, spdx_id: str, exact_match: str) -> bool:
    """Check if a file contains the SPDX license header."""
    spdx_regex = get_spdx_license_regex(file_path, spdx_id if exact_match else "")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if re.search(spdx_regex, line):
                    return True
        add_spdx_header(file_path, spdx_id)
        return False
    except (OSError, UnicodeDecodeError):
        # Skip binary files or unreadable files
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--license", type=str, help="Filenames to fix")
    parser.add_argument(
        "--exact_match", action="store_true", help="License has to match the --license exactly"
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to process.",
    )
    args = parser.parse_args()
    ret_val = 0
    for filename in args.filenames:
        res = check_spdx_header(Path(filename), args.license, args.exact_match)
        if not res:
            ret_val = 1
    return ret_val


if __name__ == "__main__":
    raise SystemExit(main())
