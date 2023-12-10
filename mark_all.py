import os
import re
from pathlib import Path

import lib.color as color
from lib.judge import JudgeProject
from lib.excel import ExcelIO


# input 1/3
project_name = ""
while project_name == "":
    project_name = color.input(f"input the project name (lab1, homework1, lab2, etc.): ", color.blue)


# preload the pattern
student_id_name_pattern = re.compile(r"""([0-9]+)(.*)""")


# input files
testcase_path = Path(f"./{project_name}/testcase")
extract_dir = Path(f"./{project_name}/extract/")
# files to generate / write
result_xlsx = Path(f"./{project_name}/result.xlsx")
temp_judge = Path(f"./tmp/{project_name}/judge/")


# no file
if not os.path.exists(testcase_path) or not os.path.isdir(testcase_path):
    raise ValueError(f"no directory called {testcase_path}")
if not os.path.exists(extract_dir) or not os.path.isdir(extract_dir):
    raise ValueError(f"no directory called {extract_dir}")


# input 2/3
yes_100_flag = color.input("skip 100 score automatically? ([y]/n): ", color.blue)
yes_100_flag = False if yes_100_flag != "" and yes_100_flag.lower()[0] == "n" else True
whole_flag = color.input("use whole files? (y/[n]): ", color.blue)
whole_flag = True if whole_flag != "" and whole_flag.lower()[0] == "y" else False

# get all files in <extract_dir> and <testcase_path>
_, all_dirs, _ = next(os.walk(extract_dir))
_, testcase_dirs, _ = next(os.walk(testcase_path))


# init JudgeProject
jp = JudgeProject(testcase_path, temp_dir_path=temp_judge)


# init excel output object
excelio = ExcelIO(result_xlsx)
excelio.score_excel_init(testcase_dirs)


# input 3/3
# if you had write some data in result_xxx.xlsx, skip them
from_where = color.input(f"from where (which index) to begin? ([{excelio.row_num + 1}] / other index number): ", color.blue)
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
        student_score: dict[str, list] = {}

        for question_name in jp.yield_judge_list(extract_dir / student):

            identify_str = f"[{num}] {student} {question_name}"
            color.print(f"get {identify_str} testcase", color.purple)

            # exec python file and test student's score
            # rough_score may not very accurate; it's only for reference!
            rough_score = jp.judge(whole_files=whole_flag)

            # skip if yes_100_flag is True and rough_score is 100
            if yes_100_flag and rough_score == 100:
                student_score[question_name] = [100, ""]
                color.print(f"{identify_str} rough score 100 (skip automatically)", color.purple)
                continue

            # give true score and reason (if not 100)
            while True:
                i = (color.input(f"give {identify_str} score (Enter = {rough_score} / number / . = show python code / ; = judge again): ", color.purple))
                if i in [";", "；"]:
                    rough_score = jp.judge()
                if i in [".", ",", "。", "，"]:
                    jp.show_in_vscode()
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
            color.print(e, color.red)
            color.input("please deal this and press enter")
