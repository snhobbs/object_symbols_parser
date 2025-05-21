"""
Parses symbol tables from object files using objdump, aggregates them,
and writes a sorted Excel (.xlsx) report by size and section.
"""


import time
import os
import subprocess
import math
import logging
from shutil import which
import pandas as pd
import numpy as np
from pathlib import Path

log_ = logging.getLogger("object_symbols_parser")


def combine_white_space(text: str) -> str:
    """Collapse all whitespace into a single space"""
    return " ".join(text.split())


def get_all_files_with_ending(directory="./", ending=".o") -> list:
    """
    Walk through all the directories under the head, return all files that have
    the specified ending
    """
    object_files = []
    for fdir, _, fnames in os.walk(Path(directory).absolute()):
        object_files.extend(
            [os.path.join(fdir, fname) for fname in fnames if fname.endswith(ending)]
        )
    return object_files


def parse_symbols_from_lines(sym_lines: list) -> pd.DataFrame:
    if len(sym_lines) == 0:
        return None
    lines = [pt[1] for pt in sym_lines]
    fnames = [pt[0] for pt in sym_lines]

    value_lines = []
    values_column = []
    for i, value in enumerate([line.split(" ")[0] for line in lines]):
        try:
            int(value, 16)
            values_column.append(value)
            value_lines.append(i)
        except (ValueError, TypeError):
            pass

    lines = [line for i, line in enumerate(lines) if i in value_lines]
    value_width = math.ceil(np.mean([len(pt) for pt in values_column]))
    group_width = 7
    group_flags = [
        line[value_width + 1 : value_width + 1 + group_width] for line in lines
    ]
    sections = [
        line[value_width + 1 + group_width + 1 :].split("\t")[0] for line in lines
    ]
    size = [line.split("\t")[1].strip().split(" ")[0] for line in lines]
    name = [" ".join(line.split("\t")[1].strip().split(" ")[1:]) for line in lines]
    return pd.DataFrame(
        {
            "name": name,
            "section": sections,
            "size": [int(pt, 16) for pt in size],
            "value": [int(pt, 16) for pt in values_column],
            "group": group_flags,
            "fname": [fnames[i] for i in value_lines],
        }
    )


def process_files(source_file, tool_chain, extensions):
    fnames = []
    for f in source_file:
        if os.path.isfile(f):
            fnames.append(f)
        elif os.path.isdir(f):
            for ext in extensions:
                fnames.extend(get_all_files_with_ending(f, ext))
    return fnames


def resolve_objdump_path(tool_chain, objdump="objdump"):
    if tool_chain:
        return str(Path(tool_chain) / objdump)
    return which(objdump) or objdump


def run_objdump_syms(fname: str, fout=None, *, tool_chain=None, objdump="objdump") -> str:
    """
    Returns the entirety of the objdump as a string
    """
    if fout is None:
        name = fname.rsplit(".", maxsplit=1)[0]
        fout = f"{name}_{int(time.time())}.syms"

    cmd = resolve_objdump_path(tool_chain, objdump=objdump)

    try:
        result = subprocess.run(
            [cmd, "--demangle", "--syms", fname],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"objdump failed: {e.stderr.strip()}") from e

    with open(fout, "w") as f:
        f.write(result.stdout)

    return result.stdout


def get_objdump_syms(source_file, tool_chain, extensions, objdump="objdump"):
    fnames = process_files(source_file, tool_chain, extensions=extensions)
    if not fnames:
        logging.error("No object files found.")
        return

    sym_lines = []

    for fname in fnames:
        objdump_output = run_objdump_syms(fname, tool_chain=tool_chain, objdump=objdump)
        sym_lines.extend((fname, line) for line in objdump_output.splitlines())

    if len(sym_lines) == 0:
        logging.error("No symbols found")
        return

    df = parse_symbols_from_lines(sym_lines)

    if df is None or df.empty:
        logging.error("No valid symbols found.")
        return

    df["section type"] = [section.strip(".").split(".")[0] for section in df["section"]]

    df.sort_values(
        by=["section type", "size"],  #  primary, secondary key
        axis=0,
        ascending=[False, False],
        inplace=True,
        kind="stable",
        ignore_index=True,
        na_position="last",
        key=None,
    )
    return df
