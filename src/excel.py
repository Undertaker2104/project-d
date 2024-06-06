from xml.etree.ElementTree import XMLParser
import zipfile

# NOTE: This is a very basic Excel parser, but should be good enough to handle
#       Actionscopes and Job Orders workbooks.

class Worksheet:
	def __init__(self, table):
		self.table = table[1:]
		self.header = table[0]
	
	def get_col_index(self, col):
		"""get value by (row, col name)"""
		return self.header.index(col)
	

class _XMLTargetSharedStrings:
	strings = []
	def data(self, data):
		self.strings.append(data)


class _XMLTargetWorksheet:
	"""Parser finite state machine"""
	table = []
	state = "initial"
	val_is_sharedString = False
	col_index = 0

	def __init__(self, sharedStrings):
		self.sharedStrings = sharedStrings

	def init_new_row(self, attrs):
		"""Create a new row of the correct length. filled with None"""
		self.table.append([None] * int(attrs["spans"][2:]))

	def update_col_state(self, attrs):
		self.col_index = ord(attrs['r'][0]) - ord('A')
		self.val_is_sharedString = attrs.get('t') == 's'

	@staticmethod
	def tag_url_stripped(tag):
		"""tags start with a schema url for some reason"""
		return tag.split('}')[-1]

	def start(self, tag, attrs):
		tag = self.tag_url_stripped(tag)
		match (self.state, tag):
			case ("initial", "sheetData"):
				self.state = tag
			case ("sheetData" | "row", "row"):
				self.state = tag
				self.init_new_row(attrs)
			case ("row" | 'c', 'c'):
				self.state = tag
				self.update_col_state(attrs)
			case ('c', 'v'):
				self.state = tag

	def data(self, data):
		match (self.state, self.val_is_sharedString):
			case ('v', False):
				self.table[-1][self.col_index] = data
			case ('v', True):
				data = self.sharedStrings[int(data)]
				self.table[-1][self.col_index] = data

	def end(self, tag):
		tag = self.tag_url_stripped(tag)
		match (self.state, tag):
			case ('v', 'c'):
				self.state = tag
			case ('c', "row"):
				self.state = tag

def open(path):
	"""Parser an Excel file and turns it into a 2D array"""
	file = zipfile.ZipFile(path)

	# parse sharedStrings
	target = _XMLTargetSharedStrings()
	parser = XMLParser(target=target)
	parser.feed(file.open("xl/sharedStrings.xml").read())

	# parse worksheet
	target = _XMLTargetWorksheet(target.strings)
	parser = XMLParser(target=target)
	parser.feed(file.open("xl/worksheets/sheet1.xml").read())

	file.close()
	return Worksheet(target.table)
