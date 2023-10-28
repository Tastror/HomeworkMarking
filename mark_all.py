import os
import re
from pathlib import Path

import lib.color as color
from lib.subprocess import exec_python_file, show_in_vscode
from lib.handle_excel import ExcelIO


# preload the pattern
filename_pattern = re.compile(r""".*?([0-9]+[a-zA-Z]*)\.(?:py|ipynb)""")
student_id_name_pattern = re.compile(r"""([0-9]+)(.*)""")


def check_which_question(prefix: str, file: str):
    res = filename_pattern.match(file)
    try:
        res = prefix + res.group(1).lower()
    except Exception:
        res = None
    return res


# define and input
temp = Path("./tmp/")
path = color.input("lab name (lab1, lab2, ...): ", color.blue)
yes_100_flag = color.input("100 score skip automatically? ([y]/n): ", color.blue)
yes_100_flag = False if yes_100_flag != "" and yes_100_flag.lower()[0] == "n" else True
testcase_path = Path(f"./{path}-testcase")


# get all files in <temp> and <testcase_path>
_, all_dirs, _ = next(os.walk(temp))
_, testcase_dirs, _ = next(os.walk(testcase_path))


# testcase_dict = {
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

# load testcase dict in <testcase_path> dirs
testcase_dict = {}
for testcase_name in testcase_dirs:
    r = testcase_dict[testcase_name] = {}  # r is a short alias
    _, _, files = next(os.walk(testcase_path / testcase_name))
    for filename in files:
        num = int(Path(filename).stem)
        r.setdefault(num, {})
        type = Path(filename).suffix
        if type == ".in":
            with open(testcase_path / testcase_name / filename) as f:
                r[num]["in"] = f.read() + '\n'
        elif type == ".out":
            with open(testcase_path / testcase_name / filename) as f:
                r[num]["out"] = f.read()
        else:
            raise ValueError(f"cannot recognize filename {testcase_path / testcase_name / filename}")


# init excel output object
score_dict = {}
excelio = ExcelIO(Path(f"./result_{path}.xlsx"))
excelio.score_excel_init(testcase_dirs)


# if you had write some data in result_xxx.xlsx, skip them
from_where = color.input(f"from where to begin? ([{excelio.row_num + 1}] / other int number): ", color.blue)
from_where = excelio.row_num + 1 if from_where == "" else int(from_where)


# loop, check and output to result_xxx.xlsx
num = 0
for student in all_dirs:
    num += 1

    # skip lower than from_where
    if num < from_where: continue

    while True:

        # start a student, get student's files
        color.print(f"\n[{num}] >>> now dealing {student}", color.blue)
        student_score = score_dict[student] = {}
        _, _, files = next(os.walk(temp / student))

        for filename in files:

            # load data from student's file
            question_name = check_which_question("hw", filename)
            identify_str = f"[{num}] {student} {question_name}"
            color.print(f"get {identify_str} testcase", color.purple)
            some_testcases = testcase_dict.get(question_name, None)
            if some_testcases is None:
                color.print("error", color.red)
                continue

            # exec python file and test student's score
            # rough_score may not very accurate; it's only for reference!
            rough_score = exec_python_file(temp / student / filename, some_testcases)

            # skip if yes_100_flag is True and rough_score is 100 
            if yes_100_flag and rough_score == 100:
                student_score[question_name] = [100, ""]
                color.print(f"{identify_str} rough score 100 (skip automatically)", color.purple)
                continue

            # give true score and reason (if not 100)
            while True:
                i = (color.input(f"give {identify_str} score (Enter = {rough_score} / number / . = show python code): ", color.purple))
                if i in [".", ",", "。", "，"]:
                    show_in_vscode(temp / student / filename)
                    continue
                try:
                    res_score = min(int(i), 100)
                except Exception:
                    res_score = rough_score
                if color.input(f"{identify_str} score: {res_score}, Yes? (Enter OK / AnyString Retry): ", color.purple) == "":
                    break
            student_score[question_name] = [res_score]
            if res_score < 100:
                reason = color.input("give the reason why not 100: ", color.purple)
                student_score[question_name].append(reason)
            else:
                student_score[question_name].append("")

        # end of a student, check if need to retry
        color.print(f"[{num}] {student}: {student_score}", color.blue)
        if color.input("OK? or Retry? (Enter OK / AnyString Retry): ") == "":
            break

    # end of a student, save to excelio
    res = student_id_name_pattern.match(student)
    excelio.score_write(res.group(2), res.group(1), 100, student_score)

    # end of a student, excelio save to file
    while True:
        try:
            excelio.dump()
            break
        except Exception as e:
            color.print(e, color.RED)
            color.input("please deal this and press enter")
