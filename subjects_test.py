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

for token in lib.trivial_tokens:
	lib.frequency_dict[token] = -1

def get_frequent_tokens(text):
	tokens = lib.tokenize(text)
	tokens = [t for t in tokens if t not in lib.trivial_tokens]
	tokens.sort(key=lib.frequency_dict.get, reverse=True)
	return tokens[0:2]

subjects = lib.actionscopes.Description.copy()
subjects = subjects.map(lambda x: [*lib.tokenize(x)])
subjects.apply(lambda x: x.sort(key=lib.frequency_dict.get, reverse=True))
subjects = subjects.map(lambda x: str.join(", ", x[0:2]))

groups = dict()
for subject, description in zip(subjects, lib.actionscopes.Description):
	if subject in groups:
		groups[subject].append(description)
	else:
		groups[subject] = [description]

groups = {k: v for (k, v) in groups.items() if len(v) > 1}

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
