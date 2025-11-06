import sys
from typing import Any

from prompt_toolkit import print_formatted_text, prompt, ANSI
from prompt_toolkit.application import get_app, Application
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession


# 注册 Ctrl+C，否则会输出一长串很烦人
kb = KeyBindings()
@kb.add('c-c')
def _(__):
    # event.app.exit(result="")  # 返回空（不可这样）
    print('\n(SIGINT) quit')
    sys.exit(0)

session = PromptSession(
    key_bindings=kb,
    complete_style=CompleteStyle.MULTI_COLUMN,
    reserve_space_for_menu=3,
)

usual_print = print_formatted_text
usual_input = session.prompt

reset, bold, _, _, underline = tuple(f"\033[{i}m" for i in range(0, 4 + 1))  # type: ignore
dark_black, dark_red, dark_green, dark_yellow, dark_blue, dark_purple, dark_cyan, dark_white = tuple(f"\033[{i}m" for i in range(30, 37 + 1))
black, red, green, yellow, blue, purple, cyan, white = tuple(f"\033[{i}m" for i in range(90, 97 + 1))

# aliases
gray = dark_black
end = reset


def format(text: Any, color: str) -> str:
    return f"{color}{text}{reset}"


def print(text: Any, color: str = reset, *args, **kargs):
    usual_print(ANSI(f"{color}{text}{reset}"), *args, **kargs)


# 在 prompt 启动时立即显示补全菜单
def _show_completion_on_start():
    app = get_app()
    app.current_buffer.start_completion(select_first=False)

def input(
    text: Any, color: str = reset,
    complete_list: list = [], complete_list_show_first: bool = True,
    *args, **kargs
) -> str:
    if len(complete_list) == 0:
        return usual_input(ANSI(f"{color}{text}{reset}"), *args, **kargs)
    else:
        wc = WordCompleter(complete_list)
        if complete_list_show_first:
            pre_run_hook = _show_completion_on_start
        else:
            pre_run_hook = None
        return usual_input(
            ANSI(f"{color}{text}{reset}"),
            completer=wc,
            complete_while_typing=True,
            pre_run=pre_run_hook,
            *args, **kargs
        )


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