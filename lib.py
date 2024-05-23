import pandas as _pd
import re

# veel voorkomende maar onbelangrijke tokens
trivial_tokens = {"aan", "bij", "na", "in", "en", "het", "van", "een", "uit", "met", "op", "niet", "de", "voor", "te", "is", "zijn", "-"}

# tokens die niet in GiGaNT staan, meer dan 3 keer in merged_data, en geen
# onderdeel/machine zijn
ignore_set = {'"', '#', '#1', '#2', '#3', '#4', '#5', '#6', '#9', '&', "'communicatie", "'wash", '(', ')', '+', '-', '->', '-en', '/', '0,37kw', '0,4', '03-2020', '07-09-2017', '1,20', '1,5', '1-5', '10x', '12cm', '14cm', '15x', '1800x310', '19cm', '1x', '2,29,1', '2-update', '2018/2019', '2019/2020', '2020/2021', '2021-2', '20x', '21cm', '24-uurs', '24-uursservice', '24h', '24u', '24uur', '24uurs', '2x', '310mm', '3x', '4,39,0', '4cm', '4gr', '4x', '5-stijl', '5-voudige', '50x', '5mm', '5x', '6x', '700x310', '8x', '9cm', '9mm', ':', '?', 'a.d.h.v', 'aan-', 'aan.', 'aansturingsprobleem', 'aanvbraag', 'actions', 'adhv', 'af.', 'afd', 'afgebroken.', 'all', 'allowed', 'aluvite', 'and', 'arno', 'asi', 'b&r', 'b=2150', 'backup', 'baelebrake', 'bale', 'ball', 'banddekken', 'bellpark', 'beneden.', 'beta', 'beveiligingsupdate', 'bindprogrammanummer', 'bizerba-programma', 'bl', 'blokeerden', 'blokkerende', 'bn-contactdefect', 'bonnie', 'boxtel', 'brandon', 'briand', 'bronbaan', 'bronze', 'bronzijde', 'c/o', 'calibratie', 'cameradefecten', 'can', 'can-bus-fout', 'casecode', 'ce-machineveiligheid', 'cees', 'cleaning', 'command', 'comp', 'concurrency', 'conferentiegesprek', 'conterra', 'contracterende', 'control', 'cpu-fout', 'cudetbezoek', 'cylinder', 'dalian', 'databaseproblemen', 'databasetime-out', 'databasetime-outs', 'decop', 'def', 'defect.', 'defekt', 'dekselsopnieuw', 'dennis', 'dienstbezoek', 'div', 'door.', 'doorlichtsensor', 'dorpsboerderijen', 'double', 'draaien.', 'draaient', 'dragernummer', 'duplicate', 'ec', 'eco', 'ed', 'edwin', 'egk', 'egmond', 'eindpositie', 'enz', 'errormelding', 'etc', 'exception', 'false', 'finished', 'flavorite', 'follow', 'for', 'fotcelkapot', 'foto`s', 'foutafhandeling', 'freq', 'fresh', 'fse-bezoek', 'fuctioneerd', 'functioneerd', 'fw', 'fw:', 'fx', 'gaats', 'garantiewerkzaamheden', 'gardens', 'geannuleerde', 'gebroken.', 'gecrashed', 'gegenerate', 'gelaste', 'geleverde', 'gerard', 'gerecovered', 'gerelateerde', 'gescant', 'gescheurd.', 'get', 'gietopdrachten', 'gipmans', 'goed.', 'goes', 'got', 'grdw', 'grijperpositie', 'grondbak,lassen', 'grondopvoer', 'gts', 'hardreset', 'heftruckservice', 'hijsassen', 'hijsbeweging', 'hlc-gegevens', 'hmi', 'hoekovergang', 'holland', 'homen', 'homepositie', 'homing', 'hoogtefout', 'horticulture', 'hydro', 'hygiene', 'id', "id's", 'idle', 'ii', 'inbedrijf', 'inbedrijfstellen', 'incl', 'inf', 'installatietijd', 'invoeropdrachten', 'invoerorders', 'invoerpositie', 'invoerproblemen', 'ip', 'ipv', 'irrigation', 'ism', 'ivm', 'javo', 'jde-update', 'kapot.', 'keerinstellingen', 'kettinggebroken', 'key-useractiviteit', 'kleurenscan', 'kleurscan', 'korto', 'kunstof', 'kwijt.', 'laad/losstation', 'lakeside', 'led-probleem', 'lee', "leeg'", 'leegdraaien', 'leegfust', 'leveren.', 'lijnnamen', 'line', 'lisa', 'll', 'lm', 'lopen.', 'm1', 'm14', 'm3', 'm5', 'm6', 'm8', 'maken.', 'malfunction', 'marcel', 'markus', 'marnix', 'marokko', 'matrix-update', 'mayer', 'mbt', 'medewerkersstatistieken', 'meer.', 'mhd', 'miami', 'migration', "mislukt'", 'missende', 'monterenvan', 'mtr', 'mucci-komkommers', 'mushrooms', 'nan', 'nav', 'netwerkstoring', 'niet.', 'nitea', 'noodinvoer', 'norman', 'nulreferentie', 'nulreferentie-uitzondering', 'nurseries', 'nursery', 'ohio', 'olaf', 'olafd', 'omprogrammeren', 'oms', 'on', 'onderdelen.', 'onderdelenaanvraag', 'onderdelenlijst', 'onderdeln', 'onderhoude', 'onderhouds', 'ondersteu=ning', 'ont-', 'op.', 'opdrachtregel', 'opf', 'opgenhof', 'ophaalactie', 'oppotprojecten', 'optimalisatielus', 'optimalisatieopdracht', 'optimalizatie', 'orderoverzicht', 'origa', 'overduw', 'overgeleven', 'overveld', 'palletiseerorders', 'parts', 'patching', 'pc-software-update', 'pc-softwarefuncties', 'pc11-defect', 'pc6', 'pe', 'pers.', 'perssectie', 'pic', 'pickproblemen', 'pietv', 'plants', 'plc', "plc's", 'plc-defect', 'plc-fout', 'plc-hardwarefout', 'plc-programma', 'plc-programmaverlies', 'plc-update', 'plotzlich', 'po#', 'po-nr', 'portugal', 'position', 'positioneerd', 'presse', 'prestatieproblemen', 'prinzen', 'problem', 'proceseenheid', 'productiegegevens', 'productieretour', 'productiezijde', 'profibus-fout', 'programma-updates', 'programmaverlies', 'programmeeruren', 'proj', 'psl', 'pu6', 'pulswaarde', 'rateld', 're:', 'read', 'reageerd', 'reedcontact', 'reedcontacten', 'reeuwijk', 'registration', 'reject', 'rejecten', 'reparen', 'request', 'reserving', 'restpunten', 'restructure', 'rfq', 'rijden.', 'rijgebied', 'ron', 'runtime-fout', 'runtimefout', 'safety', 'salesorder', 'salm', 'satteliet', 'scannerdefect', 'scannerverbinding', 'schouweenheid', 'selectieoverdracht', 'senegal', 'ser', 'serviceassistentie', 'servicebezoek', 'setup', 'skl', 'sky', 'smith', 'snelheidsroutine', 'softwarewijzigingen', "som's", 'space', 'spc', 'spc-invoerfout', 'sps', 'staan.', 'stapeld', 'stapelhoogte', 'stapleld', 'start-', 'stil.', 'storing.', 'storing:', 'strap', 'summit', 'systeemcontrole', "tag-id's", 'tbv', 'tek', 'teknr', 'testmontages', 'therm', 'thuispositie', 'timeout', 'tis', 'tomatenbeurs', 'tomatenuitwisseling', 'tomato', 'toproduction', 'tov', 'tr', 'transferorder', 'transportacties', 'transportaction', 'transportactions', 'truly', 'twin', 'u2', 'u3', 'u4', 'u8', 'uit.', 'uitvoermodus', 'uitvoeropdracht', 'uitvoeropdrachten', 'universe', 'uurs', 'v0001495', 'vacuum', 'vario', 'vb', 'vb6-label', 'vb6-update', 'vd', 'veiligheids', 'veiligheidscheck', 'veiligheidsupgrades', 'verder.', 'vereijken', 'vergeer', 'verspeenafdeling', 'vervangen.', 'verzendingsoverzicht', 'vikon', 'vinovo-updates', 'viscon', 'visualizatie', 'vitoy', 'vlc-client', 'vlc-crash', 'vlc-cursus', 'vlc-servermigratie', 'vlc-services', 'vlc-systemen', 'vlc-update', 'voertt', 'vollebrecht', 'volmelding', 'von', 'vooraankoop', 'voudige', 'vreden', 'vt', 'vtc', 'vtf', 'vvf', 'vóór', 'waardens', 'wachtpositie', 'wartung', 'wastemperaturen', 'westland', 'willem', 'windwerk', 'worden.', 'works', 'xy', 'y-als', 'yaskawa', 'z-as', 'zaaiafdeling', 'zeevliet', 'zuidgeest', 'één', '\u200b\u200ben', '–'}

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
	    and token not in ignore_set):
		parts.add(token)
