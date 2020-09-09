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
FIELDS = ["heisig_number", "keyword", "character", "stroke_count", "is_primitive", "tags", "mnemonic"]

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
	with open(args.primitives) as f:
		# FORMAT: path,keyword,stroke_count,fake_heisig,next_frame,old_path,page
		rdr = csv.DictReader(f)
		for row in rdr:
			next_frame = int(row["next_frame"])
			PRIMITIVES[next_frame].append({
				"heisig_number": row["fake_heisig"],
				"keyword": row["keyword"],
				"character": '<img src="%s"/>' % (row["path"],),
				"stroke_count": int(row["stroke_count"]),
				"is_primitive": "x",
			})

	# Finally, go through the Kanji index and generate our final index notes.
	with open(args.kanji) as f:
		# FORMAT: kanji,id_5th_ed,id_6th_ed,keyword_5th_ed,keyword_6th_ed,...
		rdr = csv.DictReader(f)

		# Sort by 6th edition keyword order...
		rows = (row for row in rdr if row["id_6th_ed"])
		rows = sorted(rows, key=lambda row: int(row["id_6th_ed"]))
		# Only do Kanji which are part of RtK 1.
		rows = (row for row in rows if int(row["id_6th_ed"]))

		for row in rows:
			heisig_number = int(row["id_6th_ed"])

			# We're only doing RtK 1 here.
			if heisig_number > LAST_KANJI:
				break

			# Is there a primitive that needs to be inserted before this kanji?
			for prim in PRIMITIVES[heisig_number]:
				yield (None, prim)

			# Okay, now yield the note for this kanji.
			note = {
				"heisig_number": heisig_number,
				"keyword": row["keyword_6th_ed"],
				"character": row["kanji"],
				"stroke_count": stroke_count(row["kanji"]),
				"is_primitive": "",
			}
			yield (heisig_number, note)


def main(args):
	if args.output:
		outf = open(args.output, "w")
	else:
		outf = sys.stdout

	# Get the lesson map to generate lesson tags. If there isn't a lesson file
	# then we don't generate lesson tags. In theory you could use this for
	# custom lessons but the idea was to just mirror the Heisig lessons.
	LESSON_BOUNDARIES = {} # {last_frame} -> lesson
	if args.lessons:
		with open(args.lessons) as f:
			# FORMAT: lesson_id,last_frame
			rdr = csv.DictReader(f)
			for row in rdr:
				last_frame = int(row["last_frame"])
				LESSON_BOUNDARIES[last_frame] = int(row["lesson_id"]) + 1
	# Start with the lowest-frame lesson.
	current_lesson = LESSON_BOUNDARIES[min(LESSON_BOUNDARIES)] - 1

	wtr = csv.DictWriter(outf, fieldnames=FIELDS)
	wtr.writeheader()
	for real_heisig, note in generate_notes(args):
		# Update lesson index.
		if real_heisig and (real_heisig - 1) in LESSON_BOUNDARIES:
				current_lesson = LESSON_BOUNDARIES[real_heisig - 1]

		# Add tags to the note.
		tags = note.get("tags", [])
		if not real_heisig:
			tags.append("primitive")
		if LESSON_BOUNDARIES:
			tags.append("lesson-%s" % (current_lesson,))
		note["tags"] = " ".join(tags)

		# Output the note.
		wtr.writerow(note)
		outf.flush()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate primitive lookup table.")
	parser.add_argument("--kanji", "-k", required=True, help="Kanji index CSV.")
	parser.add_argument("--primitives", "-p", required=True, help="Primitive index CSV.")
	parser.add_argument("--lessons", "-l", default=None, help="Lesson frames CSV.")
	parser.add_argument("--output", "-o", default=None, help="Output fileame (default: stdout).")
	main(parser.parse_args())
