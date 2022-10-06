# object_symbols_parser
Command line tool that reads object file symbol table, generate a sorted spreadsheet with the entries. Intended for embedded development where memory and code space needs to be optimized.

## Usage
### Object File
This is particularly useful if you cannot compile a binary due to the code space being exceeded.
```{bash}
object_symbols_parser.py -f src/FileSystem.o -f src/cpp_config.o -f src/main.o -o /tmp/out.xlsx
```

### ELF/AXF File
```{bash}
object_symbols_parser.py -f project.axf -o /tmp/out.xlsx
```

## Output
Generates a Pandas dataframe and saves it to a spreadsheet. By default the results are sorted as you're most likely looking for the largest entry in the symbols table.

![image](https://user-images.githubusercontent.com/20601769/194420394-d0aa33bb-4d2e-4a5e-919e-f1de119a62b0.png)

## Requirements
+ click
+ pandas
+ GNU Bintools
