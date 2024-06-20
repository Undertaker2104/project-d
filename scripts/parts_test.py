import pandas as pd
import re
import json

# veel voorkomende maar onbelangrijke tokens
trivial_tokens = {"aan", "bij", "na", "in", "en", "het", "van", "een", "uit", "met", "op", "niet", "de", "voor", "te", "is", "zijn", "-"}

# tokens die niet in GiGaNT staan, meer dan 3 keer in actionscopes, en geen
# onderdeel/machine zijn
ignore_set = {'#', '#1', '#2', '#3', '#4', '#5', '&', '(', ')', '-', '->', '+', '/', '10x', '12cm', '15x', '19cm', '1x', '2018/2019', '2019/2020', '2020/2021', '2021-2', '20x', '24-uurs', '24h', '24uurs', '2x', '3x', '4x', '5x', '50x', '6x', '8x', ':', '?', 'a.d.h.v', 'aan.', 'aanvbraag', 'adhv', 'af.', 'afd', 'afgebroken.', 'aluvite', 'arno', 'asi', 'b&r', 'bale', 'ball', 'banddekken', 'bellpark', 'beneden.', 'beta', 'bl', 'bonnie', 'boxtel', 'brandon', 'briand', 'bronbaan', 'bronze', 'c/o', 'contracterende', 'control', 'cylinder', 'dalian', 'decop', 'defect.', 'dennis', 'dienstbezoek', 'div', 'door.', 'draaien.', 'ec', 'eco', 'ed', 'edwin', 'egk', 'egmond', 'flavorite', 'for', 'foto`s', 'freq', 'fresh', 'futong', 'fw:', 'fx', 'gaats', 'gardens', 'gebroken.', 'geleverde', 'gerard', 'gescheurd.', 'gipmans', 'goed.', 'got', 'grdw', 'grondopvoer', 'gts', 'handbedien', 'hmi', 'hoekovergang', 'homen', 'homing', 'horticulture', 'hydro', 'id', "id's", 'ii', 'incl', 'ip', 'ipv', 'ivm', 'javo', 'kapot.', 'kunstof', 'kwijt.', 'laad/losstation', 'lakeside', 'led-probleem', 'leegfust', 'leveren.', 'line', 'lm', 'lopen.', 'm1', 'm14', 'm3', 'm5', 'm6', 'm8', 'maken.', 'marcel', 'markus', 'marnix', 'marokko', 'mayer', 'mbt', 'meer.', 'mhd', 'miami', 'moter', 'motor.', 'mtr', 'nan', 'nav', 'niet.', 'nitea', 'norman', 'nurseries', 'nursery', 'ohio', 'oms', 'onderdelen.', 'onderdelenaanvraag', 'onderdelenlijst', 'op.', 'opf', 'origa', 'overduw', 'parts', 'pc6', 'pers.', 'pic', 'plants', 'plc', "plc's", 'plc-fout', 'plc-programma', 'po#', 'presse', 'problem', 'proceseenheid', 'psl', 'pu6', 're:', 'read', 'reedcontact', 'reedcontacten', 'reeuwijk', 'request', 'rfq', 'rijden.', 'ron', 'safety', 'salm', 'satteliet', 'schouweenheid', 'ser', 'servicebezoek', 'skl', 'smith', 'snelheidsroutine', 'space', 'spc', 'sps', 'staan.', 'stapeld', 'stil.', 'storing.', 'storing:', 'strap', 'tbv', 'tek', 'teknr', 'tgw', 'therm', 'tifs', 'tis', 'tomatenbeurs', 'tomatenuitwisseling', 'tomato', 'tov', 'tr', 'truly', 'twin', 'u2', 'u3', 'u4', 'u8', 'uit.', 'universe', 'uurs', 'vacuum', 'vario', 'vd', 'verder.', 'vervangen.', 'vikon', 'viscon', 'vitoy', 'vollebrecht', 'von', 'voudige', 'vt', 'vtf', 'vvf', 'vóór', 'wartung', 'westland', 'windwerk', 'worden.', 'yaskawa', 'z-as', 'zaaiafdeling', 'zuidgeest'}

# GiGaNT-Molex 2.0 lexicon
# cut -f 2,5 molex_22_02_2022.tsv | tr "[:upper:]" "[:lower:]" | uniq > words.txt
lem_dict = re.split("\t|\n", open("../data/lem_dict.txt", encoding="utf-8").read())
lem_dict = {k: v for k, v in zip(lem_dict[1::2], lem_dict[0::2])}

lexicon = set(lem_dict.values())

lem_dict["hijsbanden"] = "hijsband"

def normalize(text):
    return re.sub(", |\.", ' ', str(text).lower())

def tokenize(text):
    return [lem_dict.get(t, t) for t in normalize(text).split()]

frequency_dict = dict()
def _increment_word_count(text):
    tokens = tokenize(text)
    for t in tokens:
        frequency_dict[t] = frequency_dict.get(t, 0) + 1


actionscopes = pd.read_excel("translated_actionscopes.xlsx", index_col="Code")
actionscopes.Description.apply(_increment_word_count)

parts = set()
for (token, count) in frequency_dict.items():
    if (token not in lexicon
        and count > 3
        and not token.isnumeric()
        and token not in ignore_set):
        parts.add(token)

part_groups = {p: [] for p in parts}

for code, row in actionscopes.iterrows():
    description = row["Description"]
    tokens = tokenize(description)
    for part in parts:
        if part in tokens:
            part_groups[part].append(code)

if __name__ == "__main__":
    part_groups_df = {}
    for part, codes in part_groups.items():
        # Replace invalid characters in part name
        valid_part_name = re.sub(r'[^\w\s-]', '', part)
        part_data = {"Code": codes, "Description": [actionscopes["Description"][code] for code in codes]}
        part_df = pd.DataFrame(part_data)
        part_groups_df[valid_part_name] = part_df

    # Write each part to a separate sheet in an Excel file
    with pd.ExcelWriter('output.xlsx') as writer:
        for part, df in part_groups_df.items():
            df.to_excel(writer, sheet_name=part, index=False)
