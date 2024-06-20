from xml.etree.ElementTree import XMLParser
import zipfile

# NOTE: This is a very basic Excel parser, but should be good enough to handle
#       Actionscopes and Job Orders workbooks.
#
#       Maybe store each column into a separate list. This makes more sense
#       considering the way the data is processed, simplifying logic, and
#       perhaps speeding up processing

def _tag_url_stripped(tag):
	"""tags start with a schema url for some reason"""
	return tag.split('}')[-1]

class Worksheet:
	def __init__(self, table):
		self.table = table[1:]
		self.header = table[0]
	
	def get_col_index(self, col):
		"""get value by (row, col name)"""
		return self.header.index(col)

	def guess_sheet_type(self):
		sheet_type = "unknown"
		if "Description_x" in self.header:
			sheet_type = "merged"
		elif "Actionscope.Code" in self.header:
			sheet_type = "job_order"
		elif "Code" in self.header:
			sheet_type = "actionscope"
		return sheet_type

class _XMLTargetSharedStrings:
	def __init__(self):
		self.strings = []
		self.open = False
		self.buf = ''

	# Text elements within SharedStringItems need to be joined
	# https://learn.microsoft.com/en-us/office/open-xml/spreadsheet/working-with-the-shared-string-table
	def data(self, data):
		if self.open:
			self.buf += data

	def start(self, tag, attrs):
		tag = _tag_url_stripped(tag)
		if tag == "si":
			self.open = True

	def end(self, tag):
		tag = _tag_url_stripped(tag)
		if tag == "si":
			self.strings.append(self.buf)
			self.buf = ''
			self.open = False


class _XMLTargetWorksheet:
	def __init__(self, sharedStrings):
		self.sharedStrings = sharedStrings
		self.table = []
		self.state = "initial"
		self.val_is_sharedString = False
		self.col_index = 0

	def init_new_row(self, attrs):
		"""Create a new row of the correct length. filled with None"""
		if attrs["spans"][1].isnumeric():
			self.table.append([None] * int(attrs["spans"][3:]))
		else:
			self.table.append([None] * int(attrs["spans"][2:]))

	def update_col_state(self, attrs):
		col = 0
		for c in attrs['r']:
			if c.isalpha():
				col *= 25
				col += ord(c) - ord('A')
		self.col_index = col
		self.val_is_sharedString = attrs.get('t') == 's'

	@staticmethod
	def tag_url_stripped(tag):
		"""tags start with a schema url for some reason"""
		return tag.split('}')[-1]

	def start(self, tag, attrs):
		tag = _tag_url_stripped(tag)
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
		tag = _tag_url_stripped(tag)
		match (self.state, tag):
			case ('v', 'c'):
				self.state = tag
			case ('c', "row"):
				self.state = tag

# 1. look at the column headers to decide file type
# Rows that dont refer to an actionscope codes are skipped
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
