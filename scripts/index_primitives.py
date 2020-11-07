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
import enum
import shutil
import argparse
import collections

# Primitive paths are of the form:
#    <n>-strokes/p<page>.<part>-<primitive_keyword>-<modifier-information>.svg

DIR_PATTERN = re.compile(r"^(?P<strokes>\d+)-strokes$")
FULL_PATTERN = re.compile(r"^(?:.*/)?(?P<strokes>\d+)-strokes/p(?P<page>\d+)(?P<page_part>\.\d+)?-(?P<keyword>[^-]*)(?:-(?P<modifier>.*))?\.svg$")

IN_FIELDS = ["old_path", "parent_frame", "unicode", "next_frame", "real_heisig"]
OUT_FIELDS = ["path", "unicode", "keyword", "stroke_count", "fake_heisig", "next_frame", "old_path", "page"]

PARENT_FRAME_CHAIN = "^"
PARENT_FRAME_METACHARS = [PARENT_FRAME_CHAIN]

def page(path):
	m = FULL_PATTERN.match(path)
	return int(m.group("page")) + float(m.group("page_part") or 0)


def filt(path):
	m = FULL_PATTERN.match(path)
	if m is None:
		print("Skipping %s." % (path,))
	return m is not None

def parse_primitive(primitive):
	class Parsed(object):
		exact = None
		non_print = [] # (!) and (!!)
		approx = [] # (~)

	output = Parsed()

	class ParseState(enum.Enum):
		EXACT = 1
		NON_PRINTABLE = 2
		NON_PRINTABLE_UNVERIFIED = 3
		APPROXIMATE = 4

	idx = 0
	current = ParseState.EXACT
	while idx < len(primitive):
		ch = primitive[idx]
		if ch == "!":
			idx += 1
			# Is it also unverified?
			ch2 = primitive[idx]
			if ch2 == "!":
				idx += 1
				current = ParseState.NON_PRINTABLE_UNVERIFIED
			else:
				current = ParseState.NON_PRINTABLE
			continue
		elif ch == "~":
			idx += 1
			current = ParseState.APPROXIMATE
			continue

		# Get whatever characters there are before the next meta-char.
		end = min([idx for idx in (primitive.find(ch, idx) for ch in "~!") if idx >= 0] or [None])
		part = primitive[idx:end]
		if not part:
			raise ValueError("Empty segment [%d:%d] in %r" % (idx, idx + end, primitive))

		# Add it to the return state.
		if current == ParseState.EXACT:
			if output.exact is not None:
				raise ValueError("Multiple exact matches in %r" % (primitive,))
			output.exact = part
		elif current == ParseState.NON_PRINTABLE or current == ParseState.NON_PRINTABLE_UNVERIFIED:
			output.non_print.append(part)
		elif current == ParseState.APPROXIMATE:
			output.approx.append(part)
		else:
			raise RuntimeError("Unknown state reached: %r" % (current,))

		idx += len(part)

	return output


def main(args):
	# Get all source paths.
	paths = [
		os.path.join(d, p)
		for d in os.listdir(args.src)
			if DIR_PATTERN.match(d) and os.path.isdir(os.path.join(args.src, d))
				for p in os.listdir(os.path.join(args.src, d))
					if filt(os.path.join(d, p))
	]

	# Frame lookup information to figure out the ordering of frames.
	next_frames = {} # path -> frame
	prev_primitives = collections.defaultdict(list) # frame -> [path]
	real_heisigs = {} # path -> frame

	# Unicode equivalents for SVG frames.
	unicode_primitives = {} # path -> unicode-repr

	# Frame lookup information to figure out whether a frame is a "child frame"
	# -- meaning that it is an alternative version of a numbered frame.
	parent_frames = {} # path -> frame
	child_frames = collections.defaultdict(list) # frame -> [path]
	# Order of primitives which do not have a parent frame.
	standalone_primitives = {} # path -> index
	standalone_groups = [] # [[path]]

	# Pre-load any old lookup information.
	frames_wtr = None
	if args.input:
		with open(args.input, "r", newline="") as f:
			# FORMAT: old_path,parent_frame,unicode,next_frame,real_heisig
			frames_rdr = csv.DictReader(f)
			for row in frames_rdr:
				path = row["old_path"]
				if row["parent_frame"]:
					try:
						parent_frames[path] = int(row["parent_frame"])
					except ValueError as e:
						if row["parent_frame"] not in PARENT_FRAME_METACHARS:
							raise e
						parent_frames[path] = row["parent_frame"]
				if row["unicode"]:
					unicode_primitives[path] = row["unicode"]
				next_frames[path] = int(row["next_frame"])
				if row["real_heisig"]:
					real_heisigs[path] = int(row["real_heisig"])

		f = open(args.input, "w", newline="")
		frames_wtr = csv.DictWriter(f, fieldnames=IN_FIELDS, lineterminator="\n")
		frames_wtr.writeheader()

	NEED_OPTIONAL = not args.input
	FORCE_NEXT_FRAME = os.getenv("FORCE_NEXT_FRAME") is not None
	FORCE_PARENT_FRAME = os.getenv("FORCE_PARENT_FRAME") is not None
	FORCE_UNICODE = os.getenv("FORCE_UNICODE") is not None

	# Compute the frame table -- ask in *page* order!
	for path in sorted(paths, key=page):
		# What is the *next* frame (for ordering of the deck).
		if FORCE_NEXT_FRAME or path not in next_frames:
			next_frame = input("What is the frame immediately after %s? " % (path,)).strip()
		else:
			next_frame = next_frames[path]

		next_frame = int(next_frame)
		next_frames[path] = next_frame
		prev_primitives[next_frame].append(path)
		real_heisig = real_heisigs.get(path, "")

		# What is the parent frame (for filtering and grouping of primitives).
		if FORCE_PARENT_FRAME or NEED_OPTIONAL:
			parent_frame = input("What is the parent frame of %s (blank if none)? " % (path,)).strip()
		else:
			parent_frame = parent_frames.get(path, "")

		if parent_frame:
			try:
				parent_frame = int(parent_frame)
			except ValueError as e:
				if parent_frame not in PARENT_FRAME_METACHARS:
					raise e

			if parent_frame in PARENT_FRAME_METACHARS:
				if parent_frame == PARENT_FRAME_CHAIN:
					# Add this to the parent frame's standalone_primitive group.
					#
					# TODO: Should probably double-check that we don't have a
					#       "^" after a non-standalone primitive...
					parent_group = standalone_groups.pop()
					parent_group.append(path)

					standalone_primitives[path] = len(standalone_groups)
					standalone_groups.append(parent_group)
				else:
					raise RuntimeError("Unhandled parent_frame metachar %r" % (parent_frame,))
			else:
				parent_frames[path] = parent_frame
				child_frames[parent_frame].append(path)
		else:
			standalone_primitives[path] = len(standalone_groups)
			standalone_groups.append([path])

		# What is the unicode version of this primitive (for displaying)? Note
		# that rather than just doing the obvious thing and having the unicode
		# character, several primitives have unicode representations which are:
		#
		#  * Correct but not possible to display with the Anki fonts (!).
		#  * Appear to be correct but not possible to display at all (!!).
		#  * Are approximately correct -- either they are slightly different to
		#    the Japanese primitive or have otherwise been simplified (~).
		#
		# To indicate which is the case, any such unicode character will have
		# the indicated prefix -- if no prefix is present, the field is
		# considered to be an exact representation.
		#
		# TODO: Should probably add some sort of IDS lookup data for future
		#       reference...

		if FORCE_UNICODE or NEED_OPTIONAL:
			unicode_primitive = input("What is the unicode version of %s (blank if none)? " % (path,))
		else:
			unicode_primitive = unicode_primitives.get(path, "")

		if unicode_primitive:
			# This will be parsed later to avoid deleting parts of INPUT.csv.
			unicode_primitives[path] = unicode_primitive

		if frames_wtr:
			frames_wtr.writerow({
				"old_path": path,
				"parent_frame": parent_frame,
				"unicode": unicode_primitive,
				"next_frame": next_frame,
				"real_heisig": real_heisig,
			})

	# Generate the CSV.
	os.mkdir(args.output)
	csvout = os.path.join(args.output, "PRIMITIVE_INDEX.csv")
	with open(csvout, "w", newline="") as f:
		index_wtr = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
		index_wtr.writeheader()

		for path in paths:
			m = FULL_PATTERN.match(path).groupdict()
			next_frame = next_frames[path]
			parent_frame = parent_frames.get(path)
			real_heisig = real_heisigs.get(path, "")

			# Base keyword name.
			raw_keyword = m["keyword"]

			# Create a nice keyword with the modifier.
			keyword = raw_keyword.replace("_", " ")
			modifier = m.get("modifier")
			if modifier:
				keyword += " (%s)" % (modifier.replace("-", " "))

			# A "fake" Heisig number for the primitive.
			if parent_frame and parent_frame not in PARENT_FRAME_METACHARS:
				# Child primitives get <parent>.<index>.
				fake_heisig = "%.4d.%d" % (
					parent_frame, child_frames[parent_frame].index(path) + 1,
				)
			else:
				# Standalone primitives get a dediated P<index>.
				group_idx = standalone_primitives[path]
				group = standalone_groups[group_idx]
				fake_heisig = "P-%.3d" % (group_idx + 1,)
				if len(group) > 1:
					fake_heisig += ".%d" % (group.index(path) + 1,)
				# TODO: Add real_heisig here somehow...

			# Generate a new path and copy the files.
			new_path = "mRtK6-%s-%s.svg" % (
				fake_heisig,
				raw_keyword + ("-" + m["modifier"] if m["modifier"] else ""),
			)
			shutil.copyfile(os.path.join(args.src, path),
			                os.path.join(args.output, new_path))

			unicode_primitive = unicode_primitives.get(path, "")
			if unicode_primitive:
				reprs = parse_primitive(unicode_primitive)
				if reprs.exact:
					unicode_primitive = reprs.exact
				elif reprs.non_print: # (!)
					# TODO: Make this opt-in.
					unicode_primitive = ""
				elif reprs.approx: # (~)
					# TODO: Make this opt-in.
					unicode_primitive = ""
				else:
					raise ValueError("parse_primitive returned nothing for %r" % (unicode_primitive,))

				if not unicode_primitive:
					print("Skipping %s even though %d non-printables and %d approx present." % (path, len(reprs.non_print), len(reprs.approx)))

			# Generate the entry.
			index_wtr.writerow({
				"path": new_path,
				"old_path": path,
				"unicode": unicode_primitive,
				"keyword": keyword,
				"next_frame": next_frame,
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
