import os
import math
import difflib
from pathlib import Path

import lib.color as color
from lib.excel import ExcelIO


# input
project_name = ""
while project_name == "":
    project_name = color.input(f"input the project name (lab1, homework1, lab2, etc.): ", color.blue)


# input files
extract_dir = Path(f"./{project_name}/extract/")
more_dir = Path(f"./more_diff/")
# files to generate / write
result_xlsx = Path(f"./{project_name}/diff.xlsx")


# no file
if not os.path.exists(extract_dir) or not os.path.isdir(extract_dir):
    raise ValueError(f"no directory called {extract_dir}")


# all students
_, all_students_name, _ = next(os.walk(extract_dir))
color.print(f"{len(all_students_name)} to diff", color.blue)
all_students_path = [extract_dir / i for i in all_students_name]


# more to diff
more_diff_name = []
more_diff_path = []
if os.path.exists(more_dir):
    _, all_dirs, _ = next(os.walk(more_dir))
    for d in all_dirs:
        _, homework_dirs, _ = next(os.walk(more_dir / d))
        if project_name in homework_dirs:
            more_diff_name.append(d)
            more_diff_path.append(more_dir / d / project_name)

color.print(f"use {len(more_diff_path)} more to diff", color.blue)


# merge
all_name_to_diff = all_students_name.copy()
all_name_to_diff.extend(more_diff_name)
all_path_to_diff = all_students_path.copy()
all_path_to_diff.extend(more_diff_path)


# init excel output object
excelio = ExcelIO(result_xlsx, append=False)
excelio.diff_excel_init(all_name_to_diff)


# count all
for i in range(len(all_path_to_diff)):
    for j in range(i, len(all_path_to_diff)):

        to_check = {}
        similarity_list = []

        # to lower
        _, _, files_i = next(os.walk(all_path_to_diff[i]))
        files_i_lower = [s.lower() for s in files_i]
        _, _, files_j = next(os.walk(all_path_to_diff[j]))
        files_j_lower = [s.lower() for s in files_j]
        for i_idx in range(len(files_i_lower)):
            if files_i_lower[i_idx] in files_j_lower:
                j_idx = files_j_lower.index(files_i_lower[i_idx])
                to_check.setdefault(Path(files_i_lower[i_idx]).stem, (files_i[i_idx], files_j[j_idx]))

        for stem_name, file_name_tuple in to_check.items():
            try:
                with open(all_path_to_diff[i] / file_name_tuple[0], 'r', encoding='utf-8') as f:
                    a = f.read()
                with open(all_path_to_diff[j] / file_name_tuple[1], 'r', encoding='utf-8') as f:
                    b = f.read()
                sm = difflib.SequenceMatcher(None, a, b)
                similarity = sm.ratio()
                similarity_list.append(similarity)
                excelio.diff_write(all_name_to_diff[j], all_name_to_diff[i], stem_name, similarity)
            except:
                excelio.diff_write(all_name_to_diff[j], all_name_to_diff[i], stem_name, -1)

        color.print_still(" " * (os.get_terminal_size().columns - 1))
        color.print_must_still(
            f"now {i}-{j}: {all_name_to_diff[i]}-{all_name_to_diff[j]}: {sum(similarity_list)/len(similarity_list) if len(similarity_list) > 0 else -1}",
            color.purple
        )

excelio.dump()
