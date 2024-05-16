#!/usr/bin/env python
#
# Groepeer actionscopes op onderdelen
# 1. Tokenize tekst.
# 2. Staat de token niet in de lexicon, komt vaker dan 3 keer voor, en staat
#    niet in de ignore-set? dan is het een onderdeel.
# 3. Groupeer descriptions op onderdeel.
import pandas as pd
import lib as lib

part_groups = {p: [] for p in lib.parts}

for code, row in lib.actionscopes.iterrows():
	description = row["Description"]
	tokens = lib.tokenize(description)
	for part in lib.parts:
		if part in tokens:
			part_groups[part].append(code)

if __name__ == "__main__":
	from pprint import pprint
	x = {k: [lib.actionscopes["Description"][d]
	     for d in v] for k, v in part_groups.items()}
	pprint(x)
