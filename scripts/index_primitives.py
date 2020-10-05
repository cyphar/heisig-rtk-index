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

import re
import os
import os.path
import csv
import shutil
import argparse
import collections

# Primitive paths are of the form:
#    <n>-strokes/p<page>.<part>-<primitive_keyword>-<modifier-information>.svg

DIR_PATTERN = re.compile(r"^(?P<strokes>\d+)-strokes$")
FULL_PATTERN = re.compile(r"^(?:.*/)?(?P<strokes>\d+)-strokes/p(?P<page>\d+)(?P<page_part>\.\d+)?-(?P<keyword>[^-]*)(?:-(?P<modifier>.*))?\.svg$")

IN_FIELDS = ["old_path", "new_keyword", "next_frame"]
OUT_FIELDS = ["path", "keyword", "stroke_count", "fake_heisig", "next_frame", "old_path", "page"]

def page(path):
	m = FULL_PATTERN.match(path)
	return int(m.group("page")) + float(m.group("page_part") or 0)


def filt(path):
	m = FULL_PATTERN.match(path)
	if m is None:
		print("Skipping %s." % (path,))
	return m is not None


def main(args):
	# Get all source paths.
	paths = [
		os.path.join(d, p)
		for d in os.listdir(args.src)
			if DIR_PATTERN.match(d) and os.path.isdir(os.path.join(args.src, d))
				for p in os.listdir(os.path.join(args.src, d))
					if filt(os.path.join(d, p))
	]

	# Frame lookup information.
	next_frame = {} # path -> frame
	new_keyword = {} # path -> str
	prev_primitives = collections.defaultdict(list) # frame -> [path]

	# Pre-load any old lookup information.
	frames_wtr = None
	if args.input:
		with open(args.input, "r", newline="") as f:
			# FORMAT: old_path,new_keyword,next_frame
			frames_rdr = csv.DictReader(f)
			for row in frames_rdr:
				path = row["old_path"]
				next_frame[path] = int(row["next_frame"])
				if row["new_keyword"]:
					new_keyword[path] = row["new_keyword"]

		f = open(args.input, "w", newline="")
		frames_wtr = csv.DictWriter(f, fieldnames=IN_FIELDS, lineterminator="\n")
		frames_wtr.writeheader()

	# Compute the frame table -- ask in *page* order!
	for path in sorted(paths, key=page):
		if path not in next_frame:
			frame, *keyword = input("What is the frame immediately after %s? " % (path,)).strip().split()
		else:
			frame = next_frame[path]
			keyword = new_keyword.get(path, "").split()

		frame = int(frame)
		next_frame[path] = frame
		prev_primitives[frame].append(path)

		keyword = " ".join(keyword)
		if keyword:
			new_keyword[path] = keyword

		if frames_wtr:
			frames_wtr.writerow({
				"old_path": path,
				"next_frame": frame,
				"new_keyword": keyword,
			})


	# Generate the CSV.
	os.mkdir(args.output)
	csvout = os.path.join(args.output, "PRIMITIVE_INDEX.csv")
	with open(csvout, "w", newline="") as f:
		index_wtr = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
		index_wtr.writeheader()

		for path in paths:
			m = FULL_PATTERN.match(path).groupdict()
			frame = next_frame[path]

			# Replace the keyword.
			raw_keyword = m["keyword"]
			if path in new_keyword:
				raw_keyword = new_keyword[path].replace(" ", "_")

			# Create a nice keyword with the modifier.
			keyword = raw_keyword.replace("_", " ")
			modifier = m.get("modifier")
			if modifier:
				keyword += " (%s)" % (modifier.replace("-", " "))

			# A "fake" Heisig number for the primitive.
			fake_heisig = "%.4d.%d" % (
				frame - 1, prev_primitives[frame].index(path) + 1,
			)

			# Generate a new path and copy the files.
			new_path = "mRtK6-%s-%s.svg" % (
				fake_heisig,
				raw_keyword + ("-" + m["modifier"] if m["modifier"] else ""),
			)
			shutil.copyfile(os.path.join(args.src, path),
			                os.path.join(args.output, new_path))

			# Generate the entry.
			index_wtr.writerow({
				"path": new_path,
				"old_path": path,
				"keyword": keyword,
				"next_frame": frame,
				"stroke_count": int(m["strokes"]),
				"fake_heisig": fake_heisig.lstrip("0"),
				"page": int(m["page"]),
			})

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate primitive lookup table.")
	parser.add_argument("--output", "-o", required=True, help="Output directory.")
	parser.add_argument("--input", "-i", default=None, help="Any pre-existing input information.")
	parser.add_argument("src", help="Source directory of primitive tree.")
	main(parser.parse_args())
