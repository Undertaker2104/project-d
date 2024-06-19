from database import Database
from datasets import Datasets
from enum import StrEnum, IntFlag

import excel
import getopt
import sys

# ANSI escape codes
class C(StrEnum):
	COLOR_RED          = "\33[1;34;31m"
	COLOR_YELLOW       = "\33[1;34;93m"
	COLOR_GREEN        = "\33[1;34;32m"
	COLOR_RESET        = "\33[1;34;0m"
	BOLD_SET           = "\33[1m"
	BOLD_RESET         = "\33[22m"

class Exit(IntFlag):
	SUCCESS = 0
	FAILURE = 1


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
			return Exit.SUCCESS
		case ["part" | "parts"]:
			parts = db.get_parts()
			for part in parts:
				print(part)
			return Exit.SUCCESS
		case _:
			print_error("unknown argument " + ' '.join(args))
			return Exit.FAILURE


def cmd_group(args, db):
	match (args):
		case ["keyword" | "keywords", "all"]:
			groups = db.get_keyword_groups()
			for group in groups:
				print(":\n\t".join(group))
			return Exit.SUCCESS

		case ["keyword" | "keywords", *query]:
			groups = db.get_keyword_groups_where(*query)
			if groups:
				for group in groups:
					print(":\n\t".join(group))
			else:
				print_info("There are no items that have this keyword")
			return Exit.SUCCESS

		case ["part" | "parts", "all"]:
			groups = db.get_part_groups()
			for group in groups:
				print(":\n\t".join(group))
			return Exit.SUCCESS

		case ["part" | "parts", query]:
			groups = db.get_part_groups_where(query)
			if groups:
				for group in groups:
					print(":\n\t".join(group))
			else:
				print_info("There are no items that mention this part")
			return Exit.SUCCESS

		case [_, "query"]:
			print_error("not yet implemented")
			return Exit.FAILURE
		case ["part" | "parts" | "keyword" | "keywords"]:
			print_error("missing argument [query|all]")
			return Exit.FAILURE
		case _:
			print_error("unknown argument " + ' '.join(args))
			return Exit.FAILURE


def cmd_search(args):
	print("unimplemented")


def cmd_update(args, db):
	sheet_type = None
	filename = None
	match (args):
		case ["actionscope" | "actionscopes", file]:
			sheet_type = "actionscope"
			filename = file
		case ["job_order" | "job_orders", file]:
			sheet_type = "job_order"
			filename = file
		case _:
			print_error("Incorrect usage")
			return Exit.FAILURE

	worksheet = excel.open(filename)
	table = worksheet.table
	code_col = None
	desc_col = None
	memo_col = None

	match sheet_type:
		case "actionscope":
			code_col = worksheet.get_col_index("Code")
			desc_col = worksheet.get_col_index("Description")
			memo_col = worksheet.get_col_index("Memo")
		case "job_order":
			code_col = worksheet.get_col_index("Actionscope.Code")
			desc_col = worksheet.get_col_index("Description")
			memo_col = worksheet.get_col_index("Memo")
			# Ignore job orders that don't refer to an actionscope
			table = [r for r in table if r[code_col] is not None]

	rows = db.rows_that_arent_in_table(sheet_type, code_col, table)
	if len(rows) == 0:
		print_bold("Database is already up to date.")

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
	return Exit.SUCCESS


def main():
	if len(sys.argv) < 2:
		cmd_usage(sys.argv[0])
	else:
		db = Database()
		db.open_else_create("data.db")
		try:
			opts, args = getopt.gnu_getopt(sys.argv[1:], "", longopts = [
				"skip-translation",
			])
		except getopt.Getopterror as e:
			print_error(e)
			sys.exit(Exit.FAILURE)

		status = 0
		match args:
			case ["list", *args]:
				status = cmd_list(args, db)
			case ["group", *args]:
				status = cmd_group(args, db)
			case ["search", *args]:
				status = cmd_search(args)
			case ["update", *args]:
				status = cmd_update(args, db)
			case _:
				status = cmd_usage(sys.argv[0])
		db.close()
		sys.exit(status)

if __name__ == "__main__":
	main()
