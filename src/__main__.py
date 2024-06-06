from database import Database
import excel as excel
import subjects as sub
import sys

def cmd_usage(program_name):
	print(f"usage: {program_name} [COMMAND] [FLAGS] [QUERY]")
	print("commands:")
	print("  update")
	print("  help")
	print("  list   [QUERY]")
	print("  group  [QUERY]")
	print("  search [QUERY]")

def cmd_list(args):
	print("unimplemented")

def cmd_group(args):
	print("unimplemented")

def cmd_search(args):
	print("unimplemented")

def cmd_update(args):
	if len(args) < 1:
		print("ERROR: Forgot filename", file=sys.stderr)

	sheet_type = args[0]
	filename = args[1]
	table = excel.open(filename)
	print("updating...")
	code_col = table.get_col_index("Code")
	desc_col = table.get_col_index("Description")
	db = Database()
	db.open_else_create("data.db")
	rows = db.rows_that_arent_in_table(sheet_type, code_col, table.table)
	# In order to get the keywords from text, we need to figure what tokens have
	# the highest frequency. tokenize the text, increment frequency count for
	# each token. Finally we can query the frequency for each token and find the
	# max. alternatively, we store every single token-code pair in the database
	# as well. then we can take every token in the table, and see which ones are
	# the most frequent. the frequency table could just be a view that groups and
	# counts the token-code table. dont know if performance will be good enough.

	# update token frequencies
	descs = [r[desc_col] for r in table.table]
	freqs = sub.get_token_frequencies(descs)
	db.update_token_frequencies(freqs)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		cmd_usage(sys.argv[0])
	else:
		match sys.argv[1]:
			case "list":
				cmd_list(sys.argv[2:])
			case "group":
				cmd_group(sys.argv[2:])
			case "search":
				cmd_search(sys.argv[2:])
			case "help":
				cmd_usage(sys.argv[0])
			case "update":
				cmd_update(sys.argv[2:])
