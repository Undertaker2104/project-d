#!/usr/bin/env python
#
# Groepeer actionscopes op onderdelen
# 1. Tokenize tekst.
# 2. Staat de token niet in de lexicon, komt vaker dan 3 keer voor, en staat
#    niet in de ignore-set? dan is het een onderdeel.
# 3. Groupeer descriptions op onderdeel.
import pandas as pd
import lib as lib

# groepeer onderdeel/machine met actionscope/joborder code
part_groups = {p: set() for p in lib.parts}
for code, row in lib.actionscopes.iterrows():
	tokens = set()
	tokens.update(lib.tokenize(row["Description_x"]))
	tokens.update(lib.tokenize(row["Description_y"]))

	if type(code) is str:
		for part in lib.parts:
			if part in tokens:
				part_groups[part].add(code)

def get_descriptions(k):
	vals = lib.actionscopes["Description_x"].get(k, lib.actionscopes["Description_y"].get(k))
	return {*vals} if type(vals) is pd.core.series.Series else {vals}

if __name__ == "__main__":
	import sys
	from pprint import pprint

	if len(sys.argv) < 2:
		print(f"usage {sys.argv[0]} COMMAND ARG")
		print("commands: groups, list, search [query]")

	command = sys.argv[1]
	x = {k: [get_descriptions(d) for d in v] for k, v in part_groups.items()}

	if command == "groups":
		pprint(x)

	elif command == "list":
		pprint(x.keys())

	elif command == "search":
		arg = sys.argv[2]
		y = {k: [(d, get_descriptions(d)) for d in v] for k, v in part_groups.items()}
		for part, descs in y.items():
			if len(descs) == 0:
				continue

			print(f"{part.upper()}:")
			for code, desc in descs:
				print(f"{code}: {desc}")
	else:
		print(f"invalid command '{command}'")
