# object-symbols-parser
A command-line tool that reads object file symbol tables and generates a sorted spreadsheet with the entries.
It’s particularly useful in embedded development, where optimizing memory and code space is critical.

## Usage
### Object File
This tool is useful if you cannot compile a binary due to exceeding code space
You can provide multiple object files as input and generate a sorted symbol table in a spreadsheet format.

```bash
object_symbols_parser.py -f src/FileSystem.o -f src/cpp_config.o -f src/main.o -o /tmp/out.xlsx
```

### ELF/AXF File
```{bash}
object_symbols_parser.py -f project.axf -o /tmp/out.xlsx
```

## Output
Generates a Pandas dataframe and saves it to a spreadsheet. By default the results are sorted as you're most likely looking for the largest entry in the symbols table.

![image](blinky_objects.png)

## Requirements
+ click
+ pandas
+ GNU Bintools
