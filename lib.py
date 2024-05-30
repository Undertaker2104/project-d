import pandas as _pd
import re

# veel voorkomende maar onbelangrijke tokens
trivial_tokens = set(open("trivial_tokens.txt").read().split('\n'))

# tokens die niet in GiGaNT staan, meer dan 3 keer in merged_data, en geen
# onderdeel/machine zijn
ignored_tokens = set(open("ignored_tokens.txt").read().split('\n'))

# GiGaNT-Molex 2.0 lexicon
# cut -f 2,5 molex_22_02_2022.tsv | tr "[:upper:]" "[:lower:]" | uniq > words.txt
lem_dict = re.split("\t|\n", open("lem_dict.txt").read())
lem_dict = {k: v for k, v in zip(lem_dict[1::2], lem_dict[0::2])}

lexicon = set(lem_dict.values())

lem_dict["hijsbanden"] = "hijsband"
# spellcheck
lem_dict["shuttl"] = "shuttle"
lem_dict["defekt"] = "defect"
lem_dict["camarasysteem"] = "camerasysteem"

def normalize(text):
	return re.sub("[\[\]()\?]", '', re.sub(", |\.|:|/", ' ', str(text).lower()))

def tokenize(text):
	return [lem_dict.get(t, t) for t in normalize(text).split()]

frequency_dict = dict()
def _increment_word_count(text):
	tokens = tokenize(text)
	for t in tokens:
		frequency_dict[t] = frequency_dict.get(t, 0) + 1


actionscopes = _pd.read_excel("merged_data.xlsx", index_col="Code")
actionscopes.Description_x.apply(_increment_word_count)
actionscopes.Description_y.apply(_increment_word_count)

parts = set()
for (token, count) in frequency_dict.items():
	if (token not in lexicon
	    and count > 3
	    and not token.isnumeric()
	    and token not in ignored_tokens):
		parts.add(token)
