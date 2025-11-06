import sys
import shutil

import lib.color as color


def get_key():
    if sys.platform == 'win32':
        import msvcrt
        key = msvcrt.getch()  # type: ignore
        if key == b'\x03' or key == b'\x1a':
            exit(0)
        elif key == b'\xe0':
            key = msvcrt.getch()  # type: ignore
            if key == b'H': return 'UP'
            if key == b'P': return 'DOWN'
            if key == b'M': return 'RIGHT'
            if key == b'K': return 'LEFT'
        elif key == b'\r' or key == b'\n':
            return '\n'
        # use wasd to control
        else:
            if key == b"w" or key == b"W": return 'UP'
            if key == b"s" or key == b"S": return 'DOWN'
            if key == b"d" or key == b"D": return 'RIGHT'
            if key == b"a" or key == b"A": return 'LEFT'
        try:
            return key.decode('utf-8')
        except UnicodeDecodeError:
            return ""
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x03' or ch == '\x1a':
                exit(0)
            elif ch == '\x1b':
                ch = sys.stdin.read(1)
                if ch == '[':
                    ch = sys.stdin.read(1)
                    if ch == 'A': return 'UP'
                    if ch == 'B': return 'DOWN'
                    if ch == 'C': return 'RIGHT'
                    if ch == 'D': return 'LEFT'
            # use wasd to control
            else:
                if ch == 'w' or ch == 'W': return 'UP'
                if ch == 's' or ch == 'S': return 'DOWN'
                if ch == 'd' or ch == 'D': return 'RIGHT'
                if ch == 'a' or ch == 'A': return 'LEFT'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def best_cols(items):
    tty_column = shutil.get_terminal_size().columns

    def get_need_width(cols):
        col_widths = [0] * cols
        for i, item in enumerate(items):
            col = i % cols
            display_length = len(f"{i+1}  {item}")  
            if display_length > col_widths[col]:
                col_widths[col] = display_length
        return sum(col_widths) + 2 * cols + 1

    left, right = 1, len(items)
    while left < right:
        mid = (left + right + 1) // 2
        if get_need_width(mid) > tty_column:
            right = mid - 1
        else:
            left = mid

    return left


def display_menu(items, selected_index, cols, last_new_line_time):

    if last_new_line_time > 0:
        color.cursor_up(last_new_line_time, flush=False)
        color.cursor_row_home(flush=False)

    new_line_time = 0

    col_widths = [0] * cols
    for i, item in enumerate(items):
        col = i % cols
        display_length = len(f"{i+1}  {item}")  
        if display_length > col_widths[col]:
            col_widths[col] = display_length
    col_widths = [w + 2 for w in col_widths]
    rows = (len(items) + cols - 1) // cols

    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            if idx >= len(items):
                continue
            if idx == selected_index:
                prefix = f"\033[48;5;240m{color.bold}{color.white}"
                suffix = f"{color.end}\033[0m"
            else:
                prefix = f"{color.cyan}"
                suffix = f"{color.end}"
            item_text = f"{idx+1}) {items[idx]}"
            print(f"{prefix}{item_text.ljust(col_widths[col] - 1)}{suffix} ", end="", flush=False)
        print(flush=False)
        new_line_time += 1

    prompt_data = "↑ ↓ ← → or number: select   Enter: confirm   q: quit"
    print(f"{color.white}{prompt_data}{color.end}", end="", flush=True)
    new_line_time += len(prompt_data) // shutil.get_terminal_size().columns

    return new_line_time


def select_from_list(items, cols: None | int = None):

    if not items: return None

    if cols is None:
        cols = best_cols(items)

    total = len(items)
    rows = (total + cols - 1) // cols
    row_stop_cols = total % cols
    if row_stop_cols == 0: row_stop_cols = cols

    new_line_time = 0
    selected_number = 0
    need_update = True
    last_digit = ""

    while True:
        if need_update:
            new_line_time = display_menu(
                items, selected_number, cols, new_line_time
            )
        else:
            need_update = True

        key = get_key()

        if key == 'UP':
            selected_x = selected_number // cols
            selected_y = selected_number % cols
            if selected_x > 0:
                selected_x = selected_x - 1
            elif selected_y > 0:
                selected_y = selected_y - 1
                current_rows = rows - 1 if selected_y >= row_stop_cols else rows
                selected_x = current_rows - 1
            else:
                need_update = False
                continue
            selected_number = selected_x * cols + selected_y
        elif key == 'DOWN':
            selected_x = selected_number // cols
            selected_y = selected_number % cols
            current_rows = rows - 1 if selected_y >= row_stop_cols else rows
            if selected_x < current_rows - 1:
                selected_x = selected_x + 1
            elif selected_y < cols - 1:
                selected_y = selected_y + 1
                selected_x = 0
            else:
                need_update = False
                continue
            selected_number = selected_x * cols + selected_y
        elif key == 'RIGHT':
            if selected_number < total - 1:
                selected_number = selected_number + 1
            else:
                need_update = False
                continue
        elif key == 'LEFT':
            if selected_number > 0:
                selected_number = selected_number - 1
            else:
                need_update = False
                continue

        elif key.isdigit():
            last_digit += key
            num = int(last_digit) - 1
            if 0 <= num < len(items):
                selected_number = num
            # if cannot add more digits, reset last_digit
            else:
                last_digit = key
                num = int(last_digit) - 1
                if 0 <= num < len(items):
                    selected_number = num
                else:
                    need_update = False
                    continue

        elif key == '\r' or key == '\n':
            return items[selected_number]
        elif key.lower() == 'q':
            return None

        else:
            need_update = False
            continue


if __name__ == "__main__":
    sample_items = [str(i) for i in range(2145, 2145 + 103)]
    selected = select_from_list(sample_items)
    print()
    print(f"chosen: {selected}")
