#!/usr/bin/env python
'''
Reads an object file, returns a sorted by size xlsx

'''
import click
import pandas as pd
import time
import os
import tempfile
import glob
import cxxfilt


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
    '''
    Takes a list of tuples with the origin file and the symbol entry line
    '''
    lines = {"section": [], "size": [], "name": [], "fname": [], "demangled name": []}
    #with open(fname, 'r') as f:

    for fname, line in syms:
        print(fname)
        try:
            size, section, name = read_line(line)
        except (ValueError, IndexError):
            continue

        demangled_name = name

        try:
            demangled_name = cxxfilt.demangle(name)
        except ParseError as e:
            print(e)
            pass

        lines["size"].append(size)
        lines["section"].append(section)
        lines["name"].append(name)
        lines["demangled name"].append(demangled_name)
        lines["fname"].append(fname)

    df = pd.DataFrame(lines)
    df.sort_values(by="size", axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last', ignore_index=True, key=None)
    return df


def read_objdump_syms(fname, fout=None, tool_chain="./", objdump="objdump"):
    '''
    Returns the entirety of the objdump as a string
    '''
    if fout is None:
        fout = f"{fname.rsplit('.', maxsplit=1)[0]}_{int(time.time())}.syms"
    cmd = os.path.join(tool_chain, objdump)
    command_str = f"{cmd} --syms {fname} > {fout}"
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
@click.option("--fname", "-f", required=False, default=None, multiple=True)
@click.option("--fout", "-o", default=None)
@click.option("--all-objects", is_flag=True, help="Glob current directory for all .o files")
@click.option("--tool-chain", "-t", default="")
def main(fname, fout, all_objects, tool_chain):
    '''
    Takes the toolchain as an option. If the toolchain value is none search the path instead.
    '''
    syms = []
    if all_objects:
        obj_files = get_all_files_with_ending()
        try:
            fname = list(fname)
            fname.extend(obj_files)  #  try and extend fname, this allows appending none .o files
        except TypeError:
            fname = obj_files

    for f in fname:
        fsyms = read_objdump_syms(f, tempfile.mkstemp()[1], tool_chain)
        for line in fsyms.split("\n"):
            syms.append((f, line))
    df = parse_syms(syms)
    if fout is None:
        if len(fname) == 1:
            fout = f"{fname[0].rsplit('.', maxsplit=1)[0]}_out_{int(time.time())}.xlsx"
        else:
            fout = f"{objdump}_out_{int(time.time())}.xlsx"


    df.to_excel(fout)
    print(f"Success, output saved to {fout}")


if __name__ == "__main__":
    main()
