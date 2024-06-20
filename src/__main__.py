import os
from database import Database
from datasets import Datasets
from enum import StrEnum, IntFlag
from transformers import pipeline

import logging
import translator
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

class SheetType(StrEnum):
	ACTIONSCOPE = "actionscope"
	JOB_ORDER   = "job_order"
	MERGED      = "merged"

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

		# todo: zaaier staat is een machine maar staat in het lexicon
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


def cmd_show(args, db):
	match args:
		case ["description", code]:
			descs = db.get_descriptions(code)
			if not descs:
				print_info("code wasn't found")
			else:
				for type, desc in zip(["Actionscope", "Job Order"], descs):
					print(f"{type}:\n\t{desc}")
			return Exit.SUCCESS
		case ["memo", code]:
			memos = db.get_memos(code)
			if not memos:
				print_info("code wasn't found")
			else:
				for type, memo in zip(["Actionscope", "Job Order"], memos):
					print(f"{type}:\n\t{memo}")
			return Exit.SUCCESS
		case _:
			print_error("Incorrect usage")
			return Exit.FAILURE

def cmd_search(args):
	print("unimplemented")


def cmd_ask(args, db):
	match args:
		case [code, *question]:
			qa_pipeline = pipeline(
			    "question-answering",
			    model="henryk/bert-base-multilingual-cased-finetuned-dutch-squad2",
			    tokenizer="henryk/bert-base-multilingual-cased-finetuned-dutch-squad2"
			)
			print(qa_pipeline({
			    'context': db.get_context(code),
			    'question': ' '.join(question)}).get("answer"))


def cmd_update(args, opts, db):
	filename = None

	match (args):
		case [file]:
			filename = file
		case _:
			print_error("Incorrect usage")
			return Exit.FAILURE

	skip_translation = False
	skip_summarization = False
	for o in opts:
		if "--skip-translation" in o:
			skip_translation = True
		elif "--skip-summarization" in o:
			skip_summarization = True

	worksheet = excel.open(filename)
	sheet_type = worksheet.guess_sheet_type()
	table = worksheet.table
	code_col = None
	desc_col = None
	memo_col = None
	solution_col = None

	match sheet_type:
		case SheetType.ACTIONSCOPE:
			code_col = worksheet.get_col_index("Code")
			desc_col = worksheet.get_col_index("Description")
			memo_col = worksheet.get_col_index("Memo")
		case SheetType.JOB_ORDER:
			code_col = worksheet.get_col_index("Actionscope.Code")
			desc_col = worksheet.get_col_index("Description")
			memo_col = worksheet.get_col_index("Memo")
			solution_col = worksheet.get_col_index("Realized solution")
			# Ignore job orders that don't refer to an actionscope item
			table = [r for r in table if r[code_col] is not None]
		case SheetType.MERGED:
			code_col = worksheet.get_col_index("Code")
			desc_col = worksheet.get_col_index("Description_x")
			memo_col = worksheet.get_col_index("Memo_x")
			solution_col = worksheet.get_col_index("Realized solution")


	if sheet_type == SheetType.MERGED:
		print_info(f"detected merged file. importing...")
		datasets = Datasets()
		desc_col_y = worksheet.get_col_index("Description_y")
		memo_col_y = worksheet.get_col_index("Memo_y")
		print_info("updating keywords...")
		db.update_token_frequencies(datasets, desc_col, table)
		db.update_keywords(datasets, code_col, desc_col, table)
		as_table = []
		jo_table = []
		as_col = worksheet.get_col_index("Actionscope.Code")
		for row in table:
			if len(row) < as_col and row[as_col] is not None and row[solution_col] is not None:
				jo_table.append(row)
			else:
				as_table.append(row)
		return Exit.SUCCESS
		print_info("adding actionscope rows...")
		db.rows_add_actionscope(code_col, desc_col, memo_col, as_table)
		print_info("adding job order rows...")
		db.rows_add_job_order(code_col, desc_col, memo_col, solution_col, jo_table)
		print_info("updating parts...")
		db.update_parts(datasets, code_col, desc_col, None, table)
		return Exit.SUCCESS

	print_info(f"detected {sheet_type}s file")
	rows = db.rows_that_arent_in_table(sheet_type, code_col, table)
	if len(rows) == 0:
		print_bold("Database is already up to date.")

	# It'd make more sense to store the table as a list of columns, rather than
	# a list of rows. This would allow us to pass the list with all the values
	# of a column to the processing functions, rather than passing the table and
	# the index of the column we want to process.
	else:
		datasets = Datasets()
		# preprocessing stage
		if not skip_translation:
			print_info("translating descriptions and memos...")
			translator.translate(code_col, desc_col, memo_col, table)

		# processing stage
		if not skip_summarization:
			print_info("summarizing memos...")
			match sheet_type:
				case SheetType.ACTIONSCOPE:
					db.update_summarizations_actionscopes(code_col, memo_col, table)
				case SheetType.JOB_ORDER:
					db.update_summarizations_job_orders(code_col, memo_col, solution_col, table)
			
		print_info("updating keywords...")
		db.update_token_frequencies(datasets, desc_col, table)
		db.update_keywords(datasets, code_col, desc_col, table)

		match sheet_type:
			case SheetType.ACTIONSCOPE:
				print_info("adding actionscope rows...")
				db.rows_add_actionscope(code_col, desc_col, memo_col, table)
			case SheetType.JOB_ORDER:
				print_info("adding job order rows...")
				db.rows_add_job_order(code_col, desc_col, memo_col, solution_col, table)

		print_info("updating parts...")
		db.update_parts(datasets, code_col, desc_col, solution_col, table)
		print_bold(f"successfully added {len(rows)} items to the database!")
	return Exit.SUCCESS


def main():
	# silence transformers library
	logging.disable()

	if len(sys.argv) < 2:
		cmd_usage(sys.argv[0])
	else:
		try:
			opts, args = getopt.gnu_getopt(sys.argv[1:], "", longopts = [
				"skip-translation",
				"skip-summarization",
			])
		except getopt.GetoptError as e:
			print_error(e)
			sys.exit(Exit.FAILURE)

		db = Database()
		db.open_else_create("data.db")

		status = 0
		match args:
			case ["list", *args]:
				status = cmd_list(args, db)
			case ["group", *args]:
				status = cmd_group(args, db)
			case ["search", *args]:
				status = cmd_search(args)
			case ["update", *args]:
				status = cmd_update(args, opts, db)
			case ["show", *args]:
				status = cmd_show(args, db)
			case ["ask", *args]:
				status = cmd_ask(args, db)
			case _:
				status = cmd_usage(sys.argv[0])
		db.close()
		sys.exit(status)

if __name__ == "__main__":
	main()
