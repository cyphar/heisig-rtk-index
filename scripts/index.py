#!/usr/bin/python3
# Copyright (C) 2020 Aleksa Sarai <cyphar@cyphar.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import sys
import gzip
import os.path
import argparse
import requests
import collections

from xml.etree import ElementTree

LAST_KANJI = 2200 # Only this many kanji in RtK 1.
OUT_FIELDS = ["heisig_number", "unicode", "image", "keyword", "mnemonic", "stroke_count", "is_primitive", "tags"]

KANJIDIC2_URL = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"

def save_url(url, target, chunk_size=8192):
	sys.stderr.write("[%s] -> %s " % (KANJIDIC2_URL, target))
	with open(target, "wb") as f:
		with requests.get(url, stream=True) as r:
			r.raise_for_status()
			n = 0
			for chunk in r.iter_content(chunk_size=chunk_size):
				n += f.write(chunk)
				if n > chunk_size:
					sys.stderr.write(".")
					sys.stderr.flush()
					n %= chunk_size
		sys.stderr.write(" done\n")
		sys.stderr.flush()

def parse_xmlgz(src):
	with gzip.open(src, "rb") as gzrdr:
		return ElementTree.parse(gzrdr)


def compute_stroke_counts():
	stroke_counts = {} # character -> stroke_count

	src = "kanjidic2.xml.gz"
	if not os.path.exists(src):
		save_url(KANJIDIC2_URL, src)

	kanjidic2 = parse_xmlgz(src).getroot()
	for char in kanjidic2.findall("character"):
		# We only care about first matches.
		kanji = char.find("literal").text
		stroke_count = char.find("misc").find("stroke_count").text
		# Add to the cache.
		stroke_counts[kanji] = int(stroke_count)

	return stroke_counts

STROKE_COUNTS = {} # character -> stroke_count
def stroke_count(kanji):
	global STROKE_COUNTS
	if not STROKE_COUNTS:
		STROKE_COUNTS = compute_stroke_counts()
	return STROKE_COUNTS.get(kanji)

def generate_notes(args):
	# Pre-calculate which frame boundaries have to have primitives inserted.
	PRIMITIVES = collections.defaultdict(list) # next_frame -> [primitive]
	with open(args.primitives, "r", newline="") as f:
		# FORMAT: path,unicode,keyword,stroke_count,fake_heisig,next_frame,old_path,page
		rdr = csv.DictReader(f)
		for row in rdr:
			next_frame = int(row["next_frame"])

			PRIMITIVES[next_frame].append({
				"heisig_number": row["fake_heisig"],
				"keyword": row["keyword"],
				"unicode": row["unicode"],
				"image": '<img class="rtk-primitive" src="%s"/>' % (row["path"],),
				"stroke_count": int(row["stroke_count"]),
				"is_primitive": "y",
			})

	wanted_kanji = set(range(1, LAST_KANJI + 1))
	if args.filter:
		with open(args.filter, "r") as f:
			wanted_kanji = set(int(line) for line in f)

	# Finally, go through the Kanji index and generate our final index notes.
	with open(args.kanji, "r", newline="") as f:
		# FORMAT: kanji,id_5th_ed,id_6th_ed,keyword_5th_ed,keyword_6th_ed,...
		rdr = csv.DictReader(f)

		# Sort by 6th edition keyword order...
		rows = (row for row in rdr if row["id_6th_ed"])
		rows = sorted(rows, key=lambda row: int(row["id_6th_ed"]))
		# Only do Kanji which are part of RtK 1.
		rows = (row for row in rows if int(row["id_6th_ed"]))

		last_heisig_number = 0
		for row in rows:
			heisig_number = int(row["id_6th_ed"])

			# Only generate output for wanted kanji.
			if heisig_number not in wanted_kanji:
				continue

			# Is there a primitive that needs to be inserted before this kanji?
			for skipped in range(last_heisig_number + 1, heisig_number + 1):
				for prim in PRIMITIVES[skipped]:
					yield (None, prim)

			# Okay, now yield the note for this kanji.
			note = {
				"heisig_number": heisig_number,
				"keyword": row["keyword_6th_ed"],
				"unicode": row["kanji"],
				"image": "",
				"stroke_count": stroke_count(row["kanji"]),
				"is_primitive": "",
			}
			yield (heisig_number, note)

			# Update last heisig number.
			last_heisig_number = heisig_number


def main(args):
	if args.output:
		outf = open(args.output, "w", newline="")
	else:
		outf = sys.stdout

	wtr = csv.DictWriter(outf, fieldnames=OUT_FIELDS, lineterminator="\n")
	# TODO: Make this optional.
	#wtr.writeheader()
	for real_heisig, note in generate_notes(args):
		# Add tags to the note.
		# XXX: Tags are actually fairly annoying in the Anki interface, so
		#      disable these for now.
		tags = note.get("tags", [])
		note["tags"] = " ".join(tags)

		# Output the note.
		wtr.writerow(note)
		outf.flush()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate complete RtK kanji index.")
	parser.add_argument("--filter", help="Only include kanji with this index (will still include all primitives).")
	parser.add_argument("--kanji", "-k", required=True, help="Kanji index CSV.")
	parser.add_argument("--primitives", "-p", required=True, help="Primitive index CSV.")
	parser.add_argument("--output", "-o", default=None, help="Output fileame (default: stdout).")
	main(parser.parse_args())
