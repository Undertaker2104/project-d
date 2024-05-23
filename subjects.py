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
import math

for token in lib.trivial_tokens:
	lib.frequency_dict[token] = -1

def get_frequent_tokens(text):
	tokens = lib.tokenize(text)
	tokens = [t for t in tokens if t not in lib.trivial_tokens]
	tokens.sort(key=lib.frequency_dict.get, reverse=True)
	return tokens[0:2]

subjects = lib.actionscopes.Description_x.copy()
subjects2 = lib.actionscopes.Description_y.copy()
subjects = subjects.map(lambda x: [*lib.tokenize(x)])
subjects2 = subjects2.map(lambda x: [*lib.tokenize(x)])
subjects.apply(lambda x: x.sort(key=lib.frequency_dict.get, reverse=True))
subjects2.apply(lambda x: x.sort(key=lib.frequency_dict.get, reverse=True))
subjects = subjects.map(lambda x: str.join(", ", x[0:2]))
subjects2 = subjects2.map(lambda x: str.join(", ", x[0:2]))

groups = dict()
for subject, code in zip(subjects, lib.actionscopes.index):
	if subject in groups:
		groups[subject].add(code)
	else:
		groups[subject] = {code}

for subject, code in zip(subjects2, lib.actionscopes.index):
	if subject in groups:
		groups[subject].add(code)
	else:
		groups[subject] = {code}

def desc_get(k):
	descs = set();
	for d in k:
		vals = lib.actionscopes["Description_x"][d] if d in lib.actionscopes["Description_x"] else lib.actionscopes["Description_y"][d]
		if type(vals) is pd.core.series.Series:
			descs.update(vals)
		elif type(vals) is not float:
			descs.add(vals)
	return descs

groups = {k: desc_get(v) for k, v in groups.items() if len(v) > 1}


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
