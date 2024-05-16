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

subjects = lib.actionscopes.Description.copy()
subjects = subjects.map(lambda x: [*lib.normalize(x).split()])
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
	pprint(groups)
