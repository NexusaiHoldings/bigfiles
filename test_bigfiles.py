"""Tests for bigfiles.py."""

import subprocess
import sys
import os

import pytest

from bigfiles import human_size, walk_files


def test_walk_ordering(tmp_path):
    """walk_files returns entries sortable largest-first with correct sizes."""
    (tmp_path / "small.txt").write_bytes(b"x" * 100)
    (tmp_path / "medium.txt").write_bytes(b"x" * 1000)
    (tmp_path / "large.txt").write_bytes(b"x" * 5000)

    results = walk_files(str(tmp_path))
    results.sort(key=lambda x: x[0], reverse=True)

    assert len(results) == 3
    assert results[0][0] == 5000
    assert results[1][0] == 1000
    assert results[2][0] == 100


def test_top_truncation(tmp_path):
    """--top N limits output to exactly N data rows."""
    for i in range(5):
        (tmp_path / "file{}.txt".format(i)).write_bytes(b"x" * (i + 1) * 100)

    bigfiles_path = os.path.join(os.path.dirname(__file__), "bigfiles.py")
    result = subprocess.run(
        [sys.executable, bigfiles_path, str(tmp_path), "--top", "2"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Table structure: sep, header, sep, <data rows>, sep
    # Count lines that start with '|' and are not the header row
    lines = result.stdout.strip().splitlines()
    data_rows = [
        line for line in lines
        if line.startswith("|") and "PATH" not in line and "SIZE" not in line
    ]
    assert len(data_rows) == 2


def test_human_size_formatting():
    """human_size returns correct strings for known byte values."""
    assert human_size(0) == "0 B"
    assert human_size(512) == "512 B"
    assert human_size(1024) == "1.0 KB"
    assert human_size(1536) == "1.5 KB"
    assert human_size(1048576) == "1.0 MB"
    assert human_size(1073741824) == "1.0 GB"


def test_symlinks_skipped(tmp_path):
    """walk_files skips symlinks; only the real file appears in results."""
    real_file = tmp_path / "real.txt"
    real_file.write_bytes(b"hello")

    link_file = tmp_path / "link.txt"
    link_file.symlink_to(real_file)

    results = walk_files(str(tmp_path))
    paths = [r[1] for r in results]

    assert "link.txt" not in paths
    assert "real.txt" in paths
