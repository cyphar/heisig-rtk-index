### Scripts ###

`index_primitives.py` creates a new directory (specified by `-o`) which
contains a `PRIMITIVE_INDEX.csv` file as well as nicely-named copies of all of
the primitive SVGs. You must specify the source directory as the `primitives`
directory which contains all of the `NN-strokes` subdirectories.

```shell
% ./index_primitives.py -i primitives/INPUT.csv -o _output primitives
```

`index.py` takes a `PRIMITIVE_INDEX.csv` (specified by `-p`) and
`KANJI_INDEX.csv` (specified by `-k`) and produces a complete index (by default
to `stdout` but you can save it in a file with `-o`). This complete index is
immediately usable with Anki (all of the primitive fields are replaced with
HTML references to the SVGs as images).

```shell
% ./index.py -k kanji/KANJI_INDEX.csv -p _output/PRIMITIVE_INDEX.csv -l LESSONS.csv -o INDEX.csv
```

In order to use the imported index with Anki, you need to copy all of the SVGs
into Anki's `collections.media` folder and then do a CSV import of `INDEX.csv`.
