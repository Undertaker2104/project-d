#!/usr/bin/env python
#
# Groepeer actionscopes op onderwerp (ongeveer)
# 1. Tel alle tokens die voorkomen in de descriptions kolom.
# 2. Geef tokens die vaak voorkomen een hoge score, en die weinig voorkomen een
#    lage score.
# 3. Bepaal per description de twee tokens met de hoogste scores
# 4. Groupeer descriptions met de zelfde twee "hoogste score" tokens.
# 5. Verwijder groepen waar maar 1 description in zit.

def get_token_frequencies(datasets, text):
	

def get_frequent_tokens(datasets, text):
	tokens = datasets.tokenize(text)
	tokens = [t for t in tokens if t not in datasets.trivial_tokens]
	tokens.sort(key=lib.frequency_dict.get, reverse=True)

	return tokens[0:2]
	