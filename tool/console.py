from enum import StrEnum

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
