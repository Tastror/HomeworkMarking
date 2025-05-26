import sys
from typing import Any

usual_print = print
usual_input = input

reset, bold, _, _, underline = tuple(f"\033[{i}m" for i in range(0, 4 + 1))
dark_black, dark_red, dark_green, dark_yellow, dark_blue, dark_purple, dark_cyan, dark_white = tuple(f"\033[{i}m" for i in range(30, 37 + 1))
black, red, green, yellow, blue, purple, cyan, white = tuple(f"\033[{i}m" for i in range(90, 97 + 1))

# aliases
gray = dark_black
end = reset


def format(text: Any, color: str) -> str:
    return f"{color}{text}{reset}"


def input(text: Any, color: str = reset, *args, **kargs) -> str:
    return usual_input(f"{color}{text}{reset}", *args, **kargs)


def print(text: Any, color: str = reset, *args, **kargs):
    usual_print(f"{color}{text}{reset}", *args, **kargs)


def cursor_left(n: int, flush: bool = True):
    sys.stdout.write(f"\033[{n}D")
    if flush: sys.stdout.flush()



def cursor_right(n: int, flush: bool = True):
    sys.stdout.write(f"\033[{n}C")
    if flush: sys.stdout.flush()


def cursor_row_home(flush: bool = True):
    sys.stdout.write("\033[1G")
    if flush: sys.stdout.flush()


def cursor_up(n: int, flush: bool = True):
    sys.stdout.write(f"\033[{n}A")
    if flush: sys.stdout.flush()


def cursor_down(n: int, flush: bool = True):
    sys.stdout.write(f"\033[{n}B")
    if flush: sys.stdout.flush()


def print_there(x: int, y: int, text: Any, color: str = reset, flush: bool = True):
    # \033[x;yf or \033[x;yH: move to x, y
    # \0337 or \033[s: save cursor position
    # \0338 or \033[u: restore cursor position
    # \033[xm: change to x color (0 reset, 1 bold, 4 underline, 30~37 90~97 colors)
    # \033[a;b;cm: equal to \033[am\033[bm\033[cm
    sys.stdout.write(f"\0337\033[{x};{y}f{color}{text}{reset}\0338")
    if flush: sys.stdout.flush()


def print_still(text: Any, color: str = reset, flush: bool = True):
    # \033[xA: move up x chars
    # \033[xB: move down x chars
    # \033[xC: move right x chars
    # \033[xD: move left x chars
    sys.stdout.write(f"\033[{len(text)}D{color}{text}{reset}")
    if flush: sys.stdout.flush()

def print_must_still(text: Any, color: str, flush: bool = True):
    # \033[xA: move up x chars
    # \033[xB: move down x chars
    # \033[xC: move right x chars
    # \033[xD: move left x chars
    sys.stdout.write(f"\033[{9999}D{color}{text}{reset}")
    if flush: sys.stdout.flush()