from database import Database
from datasets import Datasets
from enum import StrEnum

import excel as excel
import sys

# ANSI escape codes
class C(StrEnum):
	COLOR_RED          = "\33[1;34;31m"
	COLOR_YELLOW       = "\33[1;34;93m"
	COLOR_GREEN        = "\33[1;34;32m"
	COLOR_RESET        = "\33[1;34;0m"
	BOLD_SET           = "\33[1m"
	BOLD_RESET         = "\33[22m"

def print_error(msg):
	print(f"{C.COLOR_RED}ERROR{C.COLOR_RESET}: {msg}", file=sys.stderr)

def print_info(msg):
	print(f"{C.COLOR_YELLOW}INFO{C.COLOR_RESET}: {msg}")

def print_bold(msg):
	print(f"{C.BOLD_SET}{msg}{C.BOLD_RESET}")

def cmd_usage(program_name):
	print(f"usage: {program_name} [COMMAND] [FLAGS] [QUERY]")
	print("commands:")
	print("  update [actionscope|job_order] [filename]")
	print("  help")
	print("  list   [PARTS|KEYWORDS]")
	print("  group  [PARTS|KEYWORDS] [query|ALL]")
	print("  search [query]")


def cmd_list(args, db):
	match (args):
		case ["keyword" | "keywords"]:
			keywords = db.get_keywords()
			for keyword in keywords:
				print(keyword)
		case ["part" | "parts"]:
			parts = db.get_parts()
			for part in parts:
				print(part)
		case _:
			print_error("unknown argument " + ' '.join(args))


def cmd_group(args, db):
	match (args):
		case ["keyword" | "keywords", "all"]:
			groups = db.get_keyword_groups()
			for group in groups:
				print(":\n\t".join(group))

		case ["keyword" | "keywords", *query]:
			groups = db.get_keyword_groups_where(*query)
			if groups:
				for group in groups:
					print(":\n\t".join(group))
			else:
				print_error("There are no items that have this keyword")

		case ["part" | "parts", "all"]:
			groups = db.get_part_groups()
			for group in groups:
				print(":\n\t".join(group))

		case ["part" | "parts", query]:
			groups = db.get_part_groups_where(query)
			if groups:
				for group in groups:
					print(":\n\t".join(group))
			else:
				print_error("There are no items that mention this part")

		case [_, "query"]:
			print_error("not yet implemented")
		case ["part" | "parts" | "keyword" | "keywords"]:
			print_error("missing argument [query|all]")
		case _:
			print_error("unknown argument " + ' '.join(args))


def cmd_search(args):
	print("unimplemented")


def cmd_update(args, db):
	if len(args) < 1:
		print("ERROR: Forgot filename", file=sys.stderr)

	sheet_type = args[0]
	filename = args[1]
	worksheet = excel.open(filename)
	table = worksheet.table
	code_col = worksheet.get_col_index("Code")
	desc_col = worksheet.get_col_index("Description")
	memo_col = worksheet.get_col_index("Memo")
	rows = db.rows_that_arent_in_table(sheet_type, code_col, table)
	if len(rows) == 0:
		print_bold("Database is already up to date.")
		db.close()

	# 1. tokenize text
	# 2. count tokens, put {token, freq} in a list
	# 3. increment frequency in database by freq
	else:
		datasets = Datasets()
		# TODO: add translation step
		print_info("updating keywords...")
		db.update_token_frequencies(datasets, desc_col, table)
		db.update_keywords(datasets, code_col, desc_col, table)
		db.rows_add(sheet_type, code_col, desc_col, memo_col, table)

		print_info("updating parts...")
		db.update_parts(datasets, code_col, desc_col, table)
		print_bold(f"successfully added {len(rows)} items to the database!")
		db.close()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		cmd_usage(sys.argv[0])
	else:
		db = Database()
		db.open_else_create("data.db")
		match sys.argv[1]:
			case "list":
				cmd_list(sys.argv[2:], db)
			case "group":
				cmd_group(sys.argv[2:], db)
			case "search":
				cmd_search(sys.argv[2:])
			case "update":
				cmd_update(sys.argv[2:], db)
			case _:
				cmd_usage(sys.argv[0])
