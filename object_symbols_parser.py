#!/usr/bin/env python
'''
Reads an object file, returns a sorted by size xlsx

'''
import time
import os
import click
import pandas as pd
import tempfile
import cxxfilt
import numpy as np
import math

def combine_white_space(text):
    '''
    Replace all white space with a single space
    '''
    for ch in ['\r', '\n', '  ', '\t']:
        text = text.strip(ch)
        while text.count(ch):
            text = text.replace(ch, ' ')
    print(text)
    return text


def read_line(line):
    text = combine_white_space(line).split(' ')
    try:
        section, size_str, _, name = text[-4:]
        size = int(size_str, base=16)
    except ValueError:
        section, size_str, name = text[-3:]
        size = int(size_str, base=16)
    return size, section, name

@click.group()
class gr1:
    pass


def parse_syms(syms):
    lines = [pt[1] for pt in syms]
    fnames = [pt[0] for pt in syms]

    value_lines = []
    values_column = []
    for i, value in enumerate([line.split(' ')[0] for line in lines]):
        try:
            int(value, 16)
            values_column.append(value)
            value_lines.append(i)
        except (ValueError, TypeError):
            pass

    lines = [line for i, line in enumerate(lines) if i in value_lines]
    value_width = math.ceil(np.mean([len(pt) for pt in values_column]))
    group_width=7
    group_flags = [line[value_width+1: value_width+1+group_width] for line in lines]
    sections = [line[value_width+1+group_width+1:].split('\t')[0] for line in lines]
    size = [line.split('\t')[1].strip().split(' ')[0] for line in lines]
    name = [' '.join(line.split('\t')[1].strip().split(' ')[1:]) for line in lines]
    return pd.DataFrame(
        {"name": name,
         "section": sections,
         "size": [int(pt, 16) for pt in size],
         "value": [int(pt, 16) for pt in values_column],
         "group": group_flags,
         "fname" : [fname for i, fname in enumerate(fnames) if i in value_lines]
         })

def read_objdump_syms(fname, fout=None, tool_chain="./", objdump="objdump"):
    '''
    Returns the entirety of the objdump as a string
    '''
    if fout is None:
        name = fname.rsplit('.', maxsplit=1)[0]
        fout = f"{name}_{int(time.time())}.syms"
    cmd = os.path.join(tool_chain, objdump)
    command_str = f"{cmd} --demangle --syms {fname} > {fout}"
    os.system(command_str)
    syms = None
    with open(fout, 'r') as f:
        syms = f.read()
    return syms


def get_all_files_with_ending(directory="./", ending=".o"):
    '''
    Walk through all the directories under the head, return all files that have
    the specified ending
    '''
    object_files = []
    for fdir, _, fnames in os.walk(directory):
        object_files.extend([os.path.join(fdir, fname) for fname in fnames if fname.endswith(ending)])
    return object_files


@click.command()
@click.option("--source-file", "-f", required=False, default=None, multiple=True, help="Multiple options, if the value is a file its symbol table is read, if it is a directory then the entire directory is walked for object files")
@click.option("--fout", "-o", default=None)
@click.option("--tool-chain", "-t", default="")
def main(source_file, fout, tool_chain):
    '''
    Takes the toolchain as an option. If the toolchain value is none search the path instead.
    '''
    syms = []
    fnames = []
    for f in source_file:
        if os.path.isfile(f):
            fnames.append(f)
        else:
            obj_files = get_all_files_with_ending(f, ".o")
            fnames.extend(obj_files)

    for f in fnames:
        fsyms = read_objdump_syms(f, tempfile.mkstemp()[1], tool_chain)
        for line in fsyms.split("\n"):
            syms.append((f, line))
    df = parse_syms(syms)
    df["section type"] = [section.strip(".").split(".")[0] for section in df["section"]]
    df.sort_values(by="size", axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last', ignore_index=True, key=None)
    df.sort_values(by="section type", axis=0, ascending=False, inplace=True, kind='stable', na_position='last', ignore_index=True, key=None)

    if fout is None:
        if len(fnames) == 1:
            name = fnames[0].rsplit('.', maxsplit=1)[0]
            fout = f"{name}_out_{int(time.time())}.xlsx"
        else:
            fout = f"objdump_out_{int(time.time())}.xlsx"

    df.to_excel(fout)
    print(f"Success, output saved to {fout}")


if __name__ == "__main__":
    main()
