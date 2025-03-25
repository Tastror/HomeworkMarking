#!/usr/bin/env python3

import os
import math
import difflib
from pathlib import Path

import lib.color as color
from lib.path import very_stem, list_sorted_files, list_sorted_dirs
from lib.excel import ExcelIO


# input
project_name = ""
while project_name == "":
    project_name = color.input(f"input the project name (lab1, homework1, lab2, etc.): ", color.blue)


# input files
extract_dir = Path.cwd() / Path(f"./{project_name}/extract/")
more_dir = Path.cwd() / Path(f"./more_diff/")
# files to generate / write
result_xlsx = Path.cwd() / Path(f"./{project_name}/diff.xlsx")
result_count_xlsx = Path.cwd() / Path(f"./{project_name}/diff-count.xlsx")


# no file
if not os.path.exists(extract_dir) or not os.path.isdir(extract_dir):
    raise ValueError(f"no directory called {extract_dir}")


# all students
all_students_name = list_sorted_dirs(extract_dir)
color.print(f"{len(all_students_name)} to diff", color.blue)
all_students_path = [extract_dir / i for i in all_students_name]


# more to diff
more_diff_name = []
more_diff_path = []
if os.path.exists(more_dir):
    all_dirs = list_sorted_dirs(more_dir)
    for d in all_dirs:
        homework_dirs = list_sorted_dirs(more_dir / d)
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
excelio = ExcelIO(result_xlsx)
excelio.square_excel_init(all_name_to_diff)


similarity_count = {}
def count_sim(stem, data):
    similarity_count.setdefault(stem, [0 for _ in range(12)])
    for i in range(11):
        if data >= 1 - 0.1 * i:
            similarity_count[stem][i] += 1
            break
    similarity_count[stem][11] += 1

# count all
for i in range(len(all_path_to_diff)):
    for j in range(i + 1, len(all_path_to_diff)):

        to_check = {}
        similarity_list = []

        # to lower
        files_i = list_sorted_files(all_path_to_diff[i])
        files_i_lower = [s.lower() for s in files_i]
        files_j = list_sorted_files(all_path_to_diff[j])
        files_j_lower = [s.lower() for s in files_j]
        for i_idx in range(len(files_i_lower)):
            if files_i_lower[i_idx] in files_j_lower:
                j_idx = files_j_lower.index(files_i_lower[i_idx])
                to_check.setdefault(very_stem(files_i_lower[i_idx]), (files_i[i_idx], files_j[j_idx]))

        for stem_name, file_name_tuple in to_check.items():
            try:
                with open(all_path_to_diff[i] / file_name_tuple[0], 'r', encoding='utf-8') as f:
                    a = f.read()
                with open(all_path_to_diff[j] / file_name_tuple[1], 'r', encoding='utf-8') as f:
                    b = f.read()
                sm = difflib.SequenceMatcher(None, a, b)
                similarity = sm.ratio()
                similarity_list.append(similarity)
                excelio.write(all_name_to_diff[j], all_name_to_diff[i], stem_name, similarity)
                count_sim(stem_name, similarity)
            except:
                excelio.write(all_name_to_diff[j], all_name_to_diff[i], stem_name, -1)

        color.print_still(" " * (os.get_terminal_size().columns - 1))
        color.print_must_still(
            f"now {i}-{j}: {all_name_to_diff[i]}-{all_name_to_diff[j]}: {sum(similarity_list)/len(similarity_list) if len(similarity_list) > 0 else -1}",
            color.purple
        )

excelio.dump()



excelio = ExcelIO(result_count_xlsx)
row_name = [f'>={1 - 0.1 * i :0.1f}' for i in range(11)]
row_name.append('total')
excelio.excel_init(row_name, list(similarity_count.keys()))

for k, v in similarity_count.items():
    for i in range(11):
        excelio.write(f'>={1 - 0.1 * i :0.1f}', k, "count", v[i] if v[i] > 0 else "")
    excelio.write('total', k, "count", v[11])

excelio.dump()
