## Complete RtK-1 Index ##

This repository contains a complete index of both the *frames* (Kanji) and
*primitives* listed in James W. Heisig's "Remembering the Kanji 1" (6th
Edition). Most other indices had at least one of the following flaws:

 * Primitives were not included at all (because they cannot be represented in
   Unicode), but this makes the index useless because the whole idea behind
   Heisig is to use primitives to build up Kanji.

 * The quality of the primitive images used were ... questionable. Usually
   these were created by taking screenshots which results in the images being
   pixellated and Anki cards generated using the index will not display nicely
   in night mode.

 * They contained some form of inaccuracy (usually incorrect keywords).

To correct all of the above, I used [an existing index of the Kanji from RtK
6th Edition][base-index] and then painstakingly extracted an SVG of each
primitive so that it could be used as a scalable (and invertable) image.
Finally I wrote some scripts to help collate all of these parts into a
"primitive" index and then another script to generate a "combined" index of
both the primitives and Kanji indices.

All of these scripts and source files are available in this repository, and you
can get the final output ("INDEX.csv" along with the set of primitive SVGs) as
a zip file from the [releases page of this project][releases]. This index is intended
to be used with Anki, to allow you to import the entire index if you have a
suitable note type. Several tags are included for each card (such as whether
they are a primitive and the lesson that the frame appears in in the book).

[base-index]: https://github.com/sdcr/heisig-kanjis
[releases]: https://github.com/cyphar/heisig-rtk-index/releases

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

### Mistakes ###

While collating all of this information, I found the following mistakes in my
physical copy of RtK (at some point I'll forward these to Heisig so that they
are corrected in any future 7th edition he chooses to release):

 * 腋 is listed in Index II as a 6-stroke primitive to be found on page 125.
   This is wrong on two counts (the character clearly has more than 6 strokes
   -- it has 12, and there is no primitive on page 125 missing from the index).
   In addition, the character itself doesn't appear in RtK at all since it is
   not a part of the Joyo Kanji.

 * Index II is missing an entry for the 6-stroke "wings" primitive on page 204
   (the primitive form of "feather") even though it's listed in Index IV as a
   primitive on that page.

 * Index II is missing an entry for the 9-stroke "in a row upside down"
   primitive on page 385 (one of the primitive forms of "row") even though it's
   listed in Index IV as a primitive on that page.

### What about RtK-3? ###

At some point I will take a look at creating an index for the third volume of
RtK (if I decide to study it), but I don't own a copy and so that will have to
wait.

### License ###

The code in this repository is licensed under the GNU General Public License
version 3 (or later).

```
Copyright (C) 2020 Aleksa Sarai <cyphar@cyphar.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

The index itself is Copyright (C) 1997-2007 James W. Heisig, and all of the
glyphs are arguably some weird copyright mix based on which fonts were used to
create them.

However in order to avoid any ambiguity, and rights I have over the glyphs in
this repository are released under the [Creative Commons CC0 license][cc0].

[cc0]: https://creativecommons.org/publicdomain/zero/1.0/legalcode
