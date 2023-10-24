import sys

usual_print = print
usual_input = input

reset, bold, _, _, underline = tuple(f"\033[{i}m" for i in range(0, 4 + 1))
black, red, green, yellow, blue, purple, cyan, white = tuple(f"\033[{i}m" for i in range(90, 97 + 1))


def format(text: any, color: str) -> str:
    return f"{color}{text}{reset}"


def input(text: any, color: str = reset, *args, **kargs) -> str:
    return usual_input(f"{color}{text}{reset}", *args, **kargs)


def print(text: any, color: str = reset, *args, **kargs):
    usual_print(f"{color}{text}{reset}", *args, **kargs)


def print_there(x: int, y: int, text: any, color: str):
    # \033[x;yf or \033[x;yH: move to x, y
    # \0337 or \033[s: save cursor position
    # \0338 or \033[u: restore cursor position
    # \033[xm: change to x color (0 reset, 1 bold, 4 underline, 30~37 90~97 colors)
    # \033[a;b;cm: equal to \033[am\033[bm\033[cm
    sys.stdout.write(f"\0337\033[{x};{y}f{color}{text}{reset}\0338")
    sys.stdout.flush()


def print_still(text: any, color: str):
    # \033[xA: move up x chars
    # \033[xB: move down x chars
    # \033[xC: move right x chars
    # \033[xD: move left x chars
    sys.stdout.write(f"\033[{len(text)}D{color}{text}{reset}")
    sys.stdout.flush()
