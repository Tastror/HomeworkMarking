#!/usr/bin/env python3

import os
import re
from pathlib import Path

import lib.color as color
import lib.constant as constant
from lib.judge import JudgeProject
from lib.excel import ExcelIO
from lib.path import list_sorted_dirs
from lib.pattern import STUDENT_ID_NAME_PATTERN
from lib.choose import select_from_list
from lib.message import Message
from lib.signal import register_sigint

register_sigint()


# input 1/3
dirs = list_sorted_dirs("./", sort=False)
dirs = [i for i in dirs if i not in constant.ROOT_DIR_NOT_READ]
dirs.sort()
color.print(f"choose the project: ", color.blue)
project_name = select_from_list(dirs)
color.print(f"\nchosen: {project_name}", color.green)


# input files
testcase_path = Path(f"./{project_name}/{constant.TESTCASE_DIR}/")
message_path = testcase_path / constant.MESSAGE_FILE
extract_dir = Path(f"./{project_name}/{constant.EXTRACT_DIR}/")
# files to generate / write
result_xlsx = Path(f"./{project_name}/{constant.RESULT_EXCEL}")
temp_judge = Path(f"./{constant.TEMP_DIR}/{project_name}/judge/")


# no file
if not os.path.exists(testcase_path) or not os.path.isdir(testcase_path):
    raise ValueError(f"no directory called {testcase_path}")
if not os.path.exists(extract_dir) or not os.path.isdir(extract_dir):
    raise ValueError(f"no directory called {extract_dir}")


# input 2/3
yes_100_flag = color.input("skip 100 score automatically? ([y]/n): ", color.blue)
yes_100_flag = False if yes_100_flag != "" and yes_100_flag.lower()[0] == "n" else True
print(yes_100_flag)
whole_flag = color.input("copy all files together (if one file depend another)? ([y]/n): ", color.blue)
whole_flag = False if whole_flag != "" and whole_flag.lower()[0] == "n" else True
print(whole_flag)
message_flag = color.input("use old error message automatically? ([y]/n): ", color.blue)
message_flag = False if message_flag != "" and message_flag.lower()[0] == "n" else True
print(message_flag)
vsc_flag = color.input("open vscode when error automatically? (y/[n]): ", color.blue)
vsc_flag = True if vsc_flag != "" and vsc_flag.lower()[0] == "y" else False
print(vsc_flag)

# get all files in <extract_dir> and <testcase_path>
all_dirs = list_sorted_dirs(extract_dir)
testcase_dirs = list_sorted_dirs(testcase_path)


# init JudgeProject
jp = JudgeProject(testcase_path, temp_dir_path=temp_judge)
message = Message(message_path)


# init excel output object
excelio = ExcelIO(result_xlsx)
excelio.score_excel_init(testcase_dirs)


# input 3/3
# if you had write some data in result_xxx.xlsx, skip them
from_where = color.input(f"from where (which index) to begin? ([{excelio.row_num + 1}] / other index number) in {len(all_dirs)} students: ", color.blue)
from_where = excelio.row_num + 1 if from_where == "" else int(from_where)
print(from_where)


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

            student_score[question_name] = [100, ""]
            # rename
            sq = student_score[question_name]
            identify_str = f"[{num}] {student} {question_name}"
            color.print(f"get {identify_str} testcase", color.purple)

            # exec python file and test student's score
            # sq[0] may not very accurate; it's only for reference!
            sq[0] = jp.judge(whole_files=whole_flag)

            # skip if yes_100_flag is True and sq[0] is 100
            if yes_100_flag and sq[0] == 100:
                sq[1] = ""
                color.print(f"{identify_str} rough score 100 (skip automatically)", color.purple)
                continue

            # give true score and reason (if not 100)
            this_time_message_flag = message_flag
            this_time_vsc_flag = vsc_flag
            while True:

                # update upon each input
                message.read()
                normal_list = message.result.get("normal", [])
                question_list = message.result.get(question_name, [])
                result_list = normal_list + question_list

                color.print(
                    f"give {identify_str} score: {sq[0]}\n"
                    f'give {identify_str} comment: {"(empty)" if sq[1] == "" else sq[1]}',
                    color.purple
                )
                i = ""
                if this_time_message_flag or this_time_vsc_flag:
                    if this_time_message_flag:
                        color.print("use error message automatically", color.yellow)
                        this_time_message_flag = False
                        i = "s"
                    if this_time_vsc_flag:
                        color.print("open vscode automatically", color.yellow)
                        this_time_vsc_flag = False
                        jp.show_in_vscode()
                else:
                    color.print(
                        "input: num -> give score / str -> give comment / m -> message / . -> show python code / ; -> judge again / q -> quit",
                        color.yellow
                    )
                    i = color.input(
                        "num / str / m / . / ; / q : ",
                        color.yellow,
                        complete_list=result_list
                    )
                if i == "q":
                    break
                elif i == "m":
                    if len(result_list) == 0:
                        color.print("message file is empty", color.red)
                    else:
                        tmp_sq1 = select_from_list(result_list, cols=1); print()
                        sq[1] = tmp_sq1 if tmp_sq1 is not None else sq[1]
                elif i in [";", "；"]:
                    sq[0] = jp.judge(whole_files=whole_flag)
                elif i in [".", ",", "。", "，"]:
                    jp.show_in_vscode()
                elif i.isdigit():
                    sq[0] = int(i)
                elif i == "":
                    pass
                else:
                    sq[1] = i
                    message.read()  # 防止手动额外加了点东西被覆盖，做不到原子也尽量靠近一点
                    message.add(question_name, i)
                    message.dump()

        # end of a student, check if need to retry
        color.print(f"[{num}] {student}:\n{student_score}", color.blue)

        break_flag = False
        while True:
            r = color.input("OK / Retry (o -> OK / r -> Retry): ")
            if r == "o":
                break_flag = True
                break
            elif r == "r":
                break
            else:
                pass
        if break_flag:
            break

    # end of a student, save to excelio
    res = STUDENT_ID_NAME_PATTERN.match(student)
    assert(res is not None)
    excelio.score_write(res.group(2), int(res.group(1)), 100, student_score)

    # end of a student, excelio save to file
    while True:
        try:
            excelio.dump()
            break
        except Exception as e:
            color.print(e, color.red)
            color.input("please deal this and press enter")
