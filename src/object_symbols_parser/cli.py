"""
Parses symbol tables from object files using objdump,
aggregates them into a DataFrame, and writes a sorted Excel report
(grouped by section type, sorted by symbol size).
"""

import logging
from pathlib import Path

import click

from object_symbols_parser import get_objdump_syms

log_ = logging.getLogger("object_symbols_parser")


@click.command()
@click.option(
    "--source-file",
    "-f",
    required=False,
    default=None,
    multiple=True,
    help="Multiple options, if the value is a file its symbol table is read, if it is a directory then the entire directory is walked for object files",
)
@click.option("--fout", "-o", default=None)
@click.option("--tool-chain", "-t", default=None)
@click.option("--debug", is_flag=True)
def main(source_file, fout, tool_chain, debug):
    """
    Takes the toolchain as an option. If the toolchain value is none search the path instead.
    """
    if debug:
        log_.setLevel(logging.DEBUG)

    fout = fout or Path(source_file[0]).with_suffix(".xlsx")

    extensions=(".o", ".obj")
    df = get_objdump_syms(source_file=source_file, tool_chain=tool_chain, extensions=extensions)
    df.to_excel(fout, index=False)
    logging.info("Success, output saved to %s", fout)


if __name__ == "__main__":
    logging.basicConfig()
    main()
