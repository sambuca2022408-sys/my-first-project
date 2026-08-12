import argparse
import sys


def get_name(default_name=None):
    if default_name:
        return default_name.strip() or "Friend"
    if len(sys.argv) > 1:
        return sys.argv[1]
    try:
        name = input("What is your name? ").strip()
    except EOFError:
        name = ""
    return name or "Friend"


def main():
    parser = argparse.ArgumentParser(description="Simple greeting application")
    parser.add_argument("--name", "-n", help="Name to greet")
    args = parser.parse_args()

    name = get_name(args.name)
    print(f"Hello, {name}!")


if __name__ == "__main__":
    main()
