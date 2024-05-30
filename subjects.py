#!/usr/bin/env python
#
# Groepeer actionscopes op onderwerp (ongeveer)
# 1. Tel alle tokens die voorkomen in de descriptions kolom.
# 2. Geef tokens die vaak voorkomen een hoge score, en die weinig voorkomen een
#    lage score.
# 3. Bepaal per description de twee tokens met de hoogste scores
# 4. Groupeer descriptions met de zelfde twee "hoogste score" tokens.
# 5. Verwijder groepen waar maar 1 description in zit.
import pandas as pd
import lib as lib
import numpy as np
import math

def get_frequent_tokens(text):
	tokens = lib.tokenize(text)
	tokens = [t for t in tokens if t not in lib.trivial_tokens]
	tokens.sort(key=lib.frequency_dict.get, reverse=True)

	return tokens[0:2]
	
def get_descriptions(k):
	descs = set();
	for d in k:
		vals = lib.actionscopes["Description_x"].get(d, lib.actionscopes["Description_y"].get(d))
		if type(vals) is pd.core.series.Series:
			descs.update(vals)
		else:
			descs.add(vals)

	return descs

for token in lib.trivial_tokens:
	lib.frequency_dict[token] = -1

groups = dict()
for descriptions in [lib.actionscopes.Description_x.copy(), lib.actionscopes.Description_y.copy()]:
	subjects = descriptions.map(lib.tokenize)
	# sorteer op token frequentie
	subjects.apply(lambda x: x.sort(key=lib.frequency_dict.get, reverse=True))
	keywords_keys = subjects.map(lambda x: str.join(", ", x[0:2]))
	for keyword_key, code in zip(keywords_keys, lib.actionscopes.index):
		if keyword_key in groups:
			groups[keyword_key].add(code)
		else:
			groups[keyword_key] = {code}

groups = {k: get_descriptions(v) for k, v in groups.items() if len(v) > 1}


if __name__ == "__main__":
	from pprint import pprint
	import sys

	if "zoek" in sys.argv:
		query = input("Zoek: ")
		res = set()
		tokens = get_frequent_tokens(query)


		if len(tokens) == 1:
			for k, d in groups.items():
				for t in tokens:
					if t in k.split(", "):
						res.update(d)
		else:
			res = groups.get(str.join(", ", get_frequent_tokens(query)))

		if res:
			pprint(res)
		else:
			print("Geen resultaten")
	else:
		pprint(groups)
