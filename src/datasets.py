import pandas as _pd
import re

class Datasets:
	def __init__(self):
		self._lem_dict = None
		self._lexicon = None
		self._trivial_tokens = None
		self._ignored_tokens = None

	def trivial_tokens(self):
		# veel voorkomende maar onbelangrijke tokens
		if self._trivial_tokens is None:
			self._trivial_tokens = set(open("data/trivial_tokens.txt").read().split('\n'))
		return self._trivial_tokens

	def ignored_tokens(self):
		# tokens die niet in GiGaNT staan, meer dan 3 keer in merged_data, en geen
		# onderdeel/machine zijn
		if self._ignored_tokens is None:
			self._ignored_tokens = set(open("data/ignored_tokens.txt").read().split('\n'))
		return self._ignored_tokens

	def lem_dict(self):
		if self._lem_dict is None:
			# GiGaNT-Molex 2.0 lexicon
			# cut -f 2,5 molex_22_02_2022.tsv | tr "[:upper:]" "[:lower:]" | uniq > words.txt
			lem_dict = re.split(r"\t|\n", open("data/lem_dict.txt").read())
			lem_dict = {k: v for k, v in zip(lem_dict[1::2], lem_dict[0::2])}
			
			# spellcheck
			lem_dict["shuttl"] = "shuttle"
			lem_dict["defekt"] = "defect"
			lem_dict["camarasysteem"] = "camerasysteem"

			parts_lem = re.split(r"\t|\n", open("data/parts_lemmatization.txt").read())
			parts_lem = {k: v for k, v in zip(parts_lem[0::2], parts_lem[1::2])}
			lem_dict.update(parts_lem)
			self._lem_dict = lem_dict
		return self._lem_dict

	def lexicon(self):
		if self._lexicon is None:
			self._lexicon = set(self.lem_dict().values())
		return self._lexicon

	@staticmethod
	def normalize(text):
		return re.sub(r"[\[\]()\?]", '', re.sub(r", |\.|:|/", ' ', str(text).lower()))

	def tokenize(self, text):
		return [self.lem_dict().get(t, t) for t in self.normalize(text).split()]

