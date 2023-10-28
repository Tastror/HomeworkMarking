import subprocess

import lib.color as color


def show_in_vscode(path: str):
    subprocess.Popen(['code', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


def exec_python_file(path: str, input: dict[int, dict[str, str]]) -> int:

    right, wrong = 0, 0

    for num, inout in input.items():

        color.print(f"testing testcase {num}", color.cyan)

        # run and get output
        p = subprocess.Popen(['python', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        output, _ = p.communicate(input=bytes(inout["in"], encoding='utf-8'))
        o = str(output, encoding='utf-8').strip('\n')

        # show output
        color.print("his/her input phrases and answer:", color.cyan)
        print(o)
        color.print("right answer:", color.cyan)
        print(inout["out"])

        # check if is right (use "in", very loose)
        if inout["out"] in o:
            color.print("RIGHT", color.green)
            right += 1
        else:
            color.print("WRONG", color.red)
            wrong += 1

    # get score
    return round(right / (right + wrong) * 50 + 50) if right + wrong > 0 else 100
