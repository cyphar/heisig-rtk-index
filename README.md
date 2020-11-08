## Complete RtK-1 Index ##

This repository contains a complete index of both the *frames* (kanji) and
*primitives* listed in James W. Heisig's "Remembering the Kanji 1" (6th
Edition). Most other indices had at least one of the following flaws:

 * Primitives were not included at all (because they cannot be represented in
   Unicode), but this makes the index useless because the whole idea behind
   Heisig is to use primitives to build up kanji.

 * The quality of the primitive images used were ... questionable. Usually
   these were created by taking screenshots which results in the images being
   pixellated and Anki cards generated using the index will not display nicely
   in night mode.

 * They contained some form of inaccuracy (usually incorrect keywords).

To correct all of the above, I used [an existing index of the kanji from RtK
6th Edition][base-index] and then painstakingly extracted an SVG of each
primitive so that it could be used as a scalable (and invertable) image.
I then went through every primitive and attempted to find a corresponding
unicode version of the character which can be rendered by modern fonts (I found
some unicode codepoints which do represent primitives but are sadly not
renderable by any fonts I have -- these are kept in this repo source but aren't
in the released index zip files). Finally I wrote some scripts to help collate
all of these parts into a "primitive" index and then another script to generate
a "combined" index of both the primitives and kanji indices.

All of these scripts and source files are available in this repository, and you
can get the final output ("INDEX.csv" along with the set of primitive SVGs) as
a zip file from the [releases page of this project][releases]. This index is intended
to be used with Anki, to allow you to import the entire index if you have a
suitable note type. Several tags are included for each card (such as whether
they are a primitive and the lesson that the frame appears in in the book).

[base-index]: https://github.com/sdcr/heisig-kanjis
[releases]: https://github.com/cyphar/heisig-rtk-index/releases

### Usage ###

Run `./index.sh`.

### Anki Import ###

In order to correctly import the cards, you should create a new card type that
has some reasonable layout for the following fields:

 1. `Heisig Number`.
 2. `Character (Unicode)`.
 3. `Character (Image)`.
 4. `Keyword`.
 5. `Mnemonic` (which you fill in yourself).
 6. `Stroke Count`.
 7. `Primitive?`.

Then take the [latest zip of the index][releases], extract it and import the
`INDEX_VOL1.csv` file into Anki (make sure that your card fields are in the
same order as the above list as that is the order of the CSV columns). Then (in
order for the primitives to show up properly), copy all of the `.svg` files in
the `collections.media` folder of the zip file into your Anki
`collections.media` folder.

If you wish to make use of a more minimal set of kanji to learn (~1000), you
can instead import the `INDEX_MINIMAL.csv` file instead of `INDEX_VOL1.csv`.
This smaller set of kanji was taken from the [Refold RRTK list][refold-rrtk]
and is intended to only teach the ~1000 most used kanji in RTK order (in order
to allow you to move onto learning kanji in-context from actual vocabulary more
quickly).

You can use this deck in both "Recognition RTK" (Lazy Kanji) or "Production
RTK" (Classic RTK) mode, all that is required is that you change the card
templates to match. Here are the card templates I used for each.

[releases]: https://github.com/cyphar/heisig-rtk-index/releases
[refold-rrtk]: https://massimmersionapproach.com/table-of-contents/stage-1/practice/recognition-rtk

#### Recognition RTK (Lazy Kanji) ###

This is the technique recommended by [Refold][refold-rrtk] for starting out
learning kanji and is based on [the Lazy Kanji technique][ajatt-lazy-kanji].

[refold-rrtk]: https://massimmersionapproach.com/table-of-contents/stage-1/practice/recognition-rtk
[ajatt-lazy-kanji]: http://www.alljapaneseallthetime.com/blog/lazy-kanji-cards-a-new-srs-card-format/

<details>
<summary>Card Front</summary>

```
<div class="tags">
Minimal RtK |
{{^Primitive?}}
  <strong>#{{Heisig Number}}</strong>
{{/Primitive?}}
{{#Primitive?}}
  <em>Primitive {{Heisig Number}}</em>
{{/Primitive?}}
{{#Stroke Count}}
| <strong>{{Stroke Count}}</strong> Strokes
{{/Stroke Count}}
</div>

<div class="center">
{{#Character (Unicode)}}
<span class="mincho">{{Character (Unicode)}}</span>
<span class="comic">{{Character (Unicode)}}</span>
<br>
<span class="kyokasho">{{Character (Unicode)}}</span>
<span class="strokeorder">{{Character (Unicode)}}</span>
{{/Character (Unicode)}}

{{^Character (Unicode)}}
{{#Character (Image)}}
<span class="mincho">{{Character (Image)}}</span>
{{/Character (Image)}}
{{^Character (Image)}}
<strong><span style="color: red">CHARACTER MISSING</span></strong>
{{/Character (Image)}}
{{/Character (Unicode)}}
</div>
```

</details>

<details>
<summary>Card Back</summary>

```
{{FrontSide}}

<hr id=answer>

<div class="word">{{Keyword}}</div>

{{#Mnemonic}}
<div class="mnemonic">{{Mnemonic}}</div>
{{/Mnemonic}}
{{^Mnemonic}}
<strong><span style="color: red">You still need to fill the mnemonic field of this card!</span></strong>
{{/Mnemonic}}
```

</details>

<details>
<summary>Card Styling</summary>

```
.card {
	font-family: yumin;
	font-size: 20px;
	background-color: #FFFAF0;
	color: #2A1B0A;
	text-align: left !important;
	max-width: 650px;
	margin: 20px auto 20px auto;
	padding: 0 20px 0 20px;
}

img {
	min-width: 200px;
	min-height: 200px;
}

.nightMode img.rtk-primitive {
	filter: invert(1);
}

@font-face { font-family: yumin; src: url('_yumin.ttf'); }
@font-face { font-family: strokeorder; src: url('_strokeorder.ttf'); }
@font-face { font-family: hgrkk; src: url('_hgrkk.ttf'); }
@font-face { font-family: yugothb; src: url('_yugothb.ttc'); }

.center {
	text-align: center !important;
}

.tags {
	color:#585858;
	font-size: 16px;
}

.mincho {
	font-family: yumin;
	font-size: 125px;
}

.comic {
	font-family: yugothb;
	font-size: 125px;
}

.kyokasho {
	font-family: hgrkk;
	font-size: 125px;
}

.strokeorder {
	font-family: strokeorder;
	font-size: 125px;
}

.word {
	font-size: 27.5px;
}

.mnemonic {
	font-size: 24px;
}

.primitive {
	color: #74291c;
}

.hyper {
	color:#585858;
	text-decoration: none;
}

.hyper:hover {
	color:#000000;
	text-decoration: underline;
}
```

</details>

#### Production RTK (Classic RTK) ###

This is the methodology that Heisig recommends, and is the one that advanced
learners of Japanese using the Refold technique are suggested to use (though
note that in that case the keywords attached will be useless to you because you
already know words using these kanji!).

<details>
<summary>Card Front</summary>

```
<div class="tags">
Minimal RtK |
{{^Primitive?}}
  <strong>#{{Heisig Number}}</strong>
{{/Primitive?}}
{{#Primitive?}}
  <em>Primitive {{Heisig Number}}</em>
{{/Primitive?}}
</div>

<div class="word">{{Keyword}}</div>
```

</details>

<details>
<summary>Card Back</summary>

```
{{FrontSide}}

<hr id=answer>

<div class="tags">
{{#Stroke Count}}
<strong>{{Stroke Count}}</strong> Strokes
{{/Stroke Count}}
</div>

<div class="center">
{{#Character (Unicode)}}
<span class="mincho">{{Character (Unicode)}}</span>
<span class="comic">{{Character (Unicode)}}</span>
<br>
<span class="kyokasho">{{Character (Unicode)}}</span>
<span class="strokeorder">{{Character (Unicode)}}</span>
{{/Character (Unicode)}}

{{^Character (Unicode)}}
{{#Character (Image)}}
<span class="mincho">{{Character (Image)}}</span>
{{/Character (Image)}}
{{^Character (Image)}}
<strong><span style="color: red">CHARACTER MISSING</span></strong>
{{/Character (Image)}}
{{/Character (Unicode)}}
</div>

<div class="word">{{Keyword}}</div>

{{#Mnemonic}}
<div class="mnemonic">{{Mnemonic}}</div>
{{/Mnemonic}}
{{^Mnemonic}}
<strong><span style="color: red">You still need to fill the mnemonic field of this card!</span></strong>
{{/Mnemonic}}
```

</details>

<details>
<summary>Card Styling</summary>

```
.card {
	font-family: yumin;
	font-size: 20px;
	background-color: #FFFAF0;
	color: #2A1B0A;
	text-align: left !important;
	max-width: 650px;
	margin: 20px auto 20px auto;
	padding: 0 20px 0 20px;
}

img {
	min-width: 200px;
	min-height: 200px;
}

.nightMode img.rtk-primitive {
	filter: invert(1);
}

@font-face { font-family: yumin; src: url('_yumin.ttf'); }
@font-face { font-family: strokeorder; src: url('_strokeorder.ttf'); }
@font-face { font-family: hgrkk; src: url('_hgrkk.ttf'); }
@font-face { font-family: yugothb; src: url('_yugothb.ttc'); }

.center {
	text-align: center !important;
}

.tags {
	color:#585858;
	font-size: 16px;
}

.mincho {
	font-family: yumin;
	font-size: 125px;
}

.comic {
	font-family: yugothb;
	font-size: 125px;
}

.kyokasho {
	font-family: hgrkk;
	font-size: 125px;
}

.strokeorder {
	font-family: strokeorder;
	font-size: 125px;
}

.word {
	font-size: 27.5px;
}

.mnemonic {
	font-size: 24px;
}

.primitive {
	color: #74291c;
}

.hyper {
	color:#585858;
	text-decoration: none;
}

.hyper:hover {
	color:#000000;
	text-decoration: underline;
}
```

</details>

#### Custom Cards ####

Note that if you're creating your own custom templates you should add the
following CSS to the styling of your card (it will make the primitives show up
in a white "font" when in Anki's night mode):

```
.nightMode img.rtk-primitive {
	filter: invert(1);
}
```

Also note that some (but not all) primitives have a Unicode representation as
well as the image representation.

### Mistakes ###

While collating all of this information, I found the following mistakes in my
physical copy of RtK (at some point I'll forward these to Heisig so that they
are corrected in any future 7th edition he chooses to release):

 * 腋 is listed in Index II as a 6-stroke primitive to be found on page 125.
   This is wrong on two counts (the character clearly has more than 6 strokes
   -- it has 12, and there is no primitive on page 125 missing from the index).
   In addition, the character itself doesn't appear in RtK at all since it is
   not a part of the Jōyō Kanji.

 * Index II is missing an entry for the 6-stroke "wings" primitive on page 204
   (the primitive form of 羽 "feather") even though it's listed in Index IV as
   a primitive on that page.

 * Index II is missing an entry for the 9-stroke "in a row upside down"
   primitive on page 385 (one of the primitive forms of 业 "row") even though
   it's listed in Index IV as a primitive on that page.

 * Index II's entry for "butcher" is incorrect. Either it should be:

   - Changed to the 6-stroke primitive 刖 ("flesh + sabre") instead of 俞
	 (which includes the "meeting" primitive, making it 9 strokes). This makes
	 it consistent with all of the usages of this kanji as a primitive.

   - The primitive should be called "meeting of butchers" to match the current
	 primitive index, but then the description of 前 will need to be updated.

 * Index III incorrectly lists the radical for 輸 as 言 (rather than 車).

 * For frame 308 ("metaphor"), Heisig uses the Hanzi character "喻" rather than
   the correct Jōyō Kanji "喩". I believe this is done because you learn all of
   the needed primitives for 喻 by this point (while "喩" has components which
   don't appear to exist in other kanji -- namely 兪 instead of 俞). However
   it's still an innacuracy in the book's teaching.

 * The character 葛 in frame 492 ("kudzu") is described as using the "siesta"
   primitive (⿱曰匂) but the actual kanji uses the 曷 primitive instead (which
   isn't given a name in Heisig).

 * The "birdhouse" primitive (⿱爫冖) is rendered as though it was
   "schoolhouse" (𰃮 =⿱𭕄冖).

 * The primitive 屯 ("earthworm") is also present as "barracks" in frame 2189.
   This should probably be reordered and the corresponding stories modified.
   This happens with several other kanji present in RtK 3 (at least 莫, 疋, 也,
   而, and 巴) but that is more excusable because not they are not in the Jōyō
   Kanji list.

 * 尗 is used in at least two kanji (戚 and 叔), maybe it should be turned into
   a primitive to make it simpler to remember? Though to be fair it doesn't
   appear to be widely used outside of those two kanji...

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
