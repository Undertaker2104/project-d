#!/usr/bin/env python
#
# Groepeer actionscopes op onderdelen
# 1. Tokenize tekst.
# 2. Staat de token niet in de lexicon, komt vaker dan 3 keer voor, en staat
#    niet in de ignore-set? dan is het een onderdeel.
# 3. Groupeer descriptions op onderdeel.
import pandas as pd
import lib as lib

part_groups = {p: set() for p in lib.parts}

for code, row in lib.actionscopes.iterrows():
	description_x = row["Description_x"]
	description_y = row["Description_y"]
	tokens = set(lib.tokenize(description_x));
	tokens.update(lib.tokenize(description_y))
	if type(code) is str:
		for part in lib.parts:
			if part in tokens:
				part_groups[part].add(code)

def desc_get(k):
	vals = lib.actionscopes["Description_x"][k] if k in lib.actionscopes["Description_x"] else lib.actionscopes["Description_y"][k]
	return {*vals} if type(vals) is pd.core.series.Series else [vals]

if __name__ == "__main__":
	from pprint import pprint
	x = {k: [desc_get(d) for d in v] for k, v in part_groups.items()}
	pprint(x)
