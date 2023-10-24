import os
import re
import subprocess
from pathlib import Path

from src.handle_excel import ExcelIO


def print_color(text, color, *args, **kargs):
    print(f"\033[{color}m{text}\033[0m", *args, **kargs)


def exec_python_file(path: str, input: dict):
    right, wrong = 0, 0
    for num, inout in input.items():
        print_color(f"testing testcase {num}", 96)
        p = subprocess.Popen(['python', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, _ = p.communicate(input=bytes(inout["in"], encoding='utf-8'))
        o = str(output, encoding='utf-8')
        print_color("his/her input phrases and answer:", 96)
        print(o.strip('\n'))
        print_color("right answer:", 96)
        print(inout["out"])
        if inout["out"] in o:
            print_color("RIGHT", 92)
            right += 1
        else:
            print_color("WRONG", 91)
            wrong += 1
    return round(right / (right + wrong) * 50 + 50) if right + wrong > 0 else 100


def check_which_question(prefix: str, file: str):
    data = re.compile(r""".*?([0-9]+[a-zA-Z]*)\.py""")
    res = data.match(file)
    try:
        res = prefix + res.group(1)
    except Exception:
        res = None
    return res


temp = Path("./tmp/")
excel = Path("./result_excel.xlsx")
path = input("\033[94mlab name (lab1, lab2, ...): \033[0m")
testcase_path = Path(f"./{path}-testcase")
_, all_dirs, _ = next(os.walk(temp))
_, testcase_dirs, _ = next(os.walk(testcase_path))

# {
#   testcase1: {
#     1: {
#       in: '123\n3456\n',
#       out: '123'
#     }
#   },
#   testcase2: {
#     1: {
#       in: '123\n21\n',
#       out: '123'
#     }
#   },
# }
testcase_dict = {}

for testcase_name in testcase_dirs:
    r = testcase_dict[testcase_name] = {}  # r is a short alias
    _, _, files = next(os.walk(testcase_path / testcase_name))
    for i in files:
        num = int(Path(i).stem)
        r.setdefault(num, {})
        type = Path(i).suffix
        if type == ".in":
            with open(testcase_path / testcase_name / i) as f:
                r[num]["in"] = f.read() + '\n'
        elif type == ".out":
            with open(testcase_path / testcase_name / i) as f:
                r[num]["out"] = f.read()
        else:
            raise ValueError(f"cannot recognize filename {testcase_path / testcase_name / i}")


score_dict = {}
excelio = ExcelIO(excel, len(testcase_dirs))
num = 0
for student in all_dirs:
    num += 1
    while True:
        print_color(f"\n[{num}] >>> now dealing {student}", 94)
        student_score = score_dict[student] = {}
        _, _, files = next(os.walk(temp / student))
        for i in files:
            question_name = check_which_question("hw", i)
            print_color(f"get {question_name} testcase", 95)
            n = testcase_dict.get(question_name, None)
            if n is None:
                print_color("error", 91)
                continue
            score = exec_python_file(temp / student / i, n)
            while True:
                print_color(f"please give {question_name} score (Enter = {score}): ", 95, end="")
                try:
                    res_score = min(int(input()), 100)
                except Exception:
                    res_score = score
                print_color(f"score: {res_score}, Yes? (Enter OK / AnyString Retry): ", 95, end="")
                if input() == "": break
            student_score[question_name] = [res_score]
            if res_score < 100:
                print_color(f"please give the reason: ", 95, end="")
                reason = input()
                student_score[question_name].append(reason)
            else:
                student_score[question_name].append("")
        print_color(f"{student}: {student_score}", 94)
        print("OK? or Retry? (Enter OK / AnyString Retry): ", end="")
        if input() == "": break
        excelio.append()

print(score_dict)
