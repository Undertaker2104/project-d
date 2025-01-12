import re


class Datasets:
    def __init__(self):
        self._lem_dict = None
        self._lexicon = None
        self._trivial_tokens = None
        self._ignored_tokens = None
        self._parts_that_are_in_lexicon = None

    def trivial_tokens(self):
        # veel voorkomende maar onbelangrijke tokens
        if self._trivial_tokens is None:
            with open("data/trivial_tokens.txt", encoding="utf-8") as file:
                self._trivial_tokens = set(file.read().split('\n'))
        return self._trivial_tokens

    def ignored_tokens(self):
        # tokens die niet in GiGaNT staan, meer dan 3 keer in merged_data, en geen
        # onderdeel/machine zijn
        if self._ignored_tokens is None:
            with open("data/ignored_tokens.txt", encoding="utf-8") as file:
                self._ignored_tokens = set(file.read().split('\n'))
        return self._ignored_tokens

    def parts_that_are_in_lexicon(self):
        if self._parts_that_are_in_lexicon is None:
            with open("data/parts_that_are_in_lexicon.txt", encoding="utf-8") as file:
                self._parts_that_are_in_lexicon = set(file.read().split('\n'))
        return self._parts_that_are_in_lexicon

    def lem_dict(self):
        if self._lem_dict is None:
            # GiGaNT-Molex 2.0 lexicon
            # cut -f 2,5 molex_22_02_2022.tsv | tr "[:upper:]" "[:lower:]" | uniq > words.txt
            with open("data/lem_dict.txt", encoding="utf-8") as file:
                lem_dict = re.split(r"\t|\n", file.read())
            lem_dict = {k: v for k, v in zip(lem_dict[1::2], lem_dict[0::2])}

            # spellcheck
            lem_dict["shuttl"] = "shuttle"
            lem_dict["defekt"] = "defect"
            lem_dict["camarasysteem"] = "camerasysteem"

            with open("data/parts_lemmatization.txt", encoding="utf-8") as file:
                parts_lem = re.split(r"\t|\n", file.read())
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
