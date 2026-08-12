
import sys

def get_name():
	# 1) If a command-line argument is provided, use it.
	if len(sys.argv) > 1:
		return sys.argv[1]
	# 2) Otherwise prompt the user (works interactively).
	try:
		name = input("What is your name? ").strip()
	except EOFError:
		name = ""
	# 3) Fall back to a default if nothing was entered.
	return name or "Friend"


if __name__ == "__main__":
	name = get_name()
	print(f"Hello, {name}!")