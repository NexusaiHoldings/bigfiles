"""bigfiles.py — walk a directory and print the N largest files in an ASCII table."""

import argparse
import os


def human_size(n):
    """Convert bytes to a human-readable string using 1024 divisor."""
    if n < 1024:
        return "{} B".format(n)
    for unit in ("KB", "MB", "GB", "TB"):
        n = n / 1024.0
        if n < 1024 or unit == "TB":
            return "{:.1f} {}".format(n, unit)


def walk_files(root):
    """Walk root (no symlinks); return list of (size, relative_path) tuples."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if os.path.islink(full_path):
                continue
            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue
            rel_path = os.path.relpath(full_path, root)
            results.append((size, rel_path))
    return results


def print_table(rows):
    """Print an ASCII table with SIZE (right-aligned) and PATH (left-aligned) columns."""
    size_header = "SIZE"
    path_header = "PATH"

    size_strings = [human_size(r[0]) for r in rows]

    size_col_width = max(
        len(size_header),
        max((len(s) for s in size_strings), default=0),
    )
    path_col_width = max(
        len(path_header),
        max((len(r[1]) for r in rows), default=0),
    )

    sep = "+-{}-+-{}-+".format("-" * size_col_width, "-" * path_col_width)

    def fmt_row(size_str, path_str):
        return "| {:>{sw}} | {:<{pw}} |".format(
            size_str, path_str, sw=size_col_width, pw=path_col_width
        )

    print(sep)
    print(fmt_row(size_header, path_header))
    print(sep)
    for size_str, (_, path) in zip(size_strings, rows):
        print(fmt_row(size_str, path))
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Print the N largest files under a directory."
    )
    parser.add_argument("directory", help="Root directory to search")
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        metavar="N",
        help="Number of largest files to show (default: 20)",
    )
    args = parser.parse_args()

    files = walk_files(args.directory)
    files.sort(key=lambda x: x[0], reverse=True)
    files = files[: args.top]
    print_table(files)


if __name__ == "__main__":
    main()
