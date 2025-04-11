#!/usr/bin/env python3

import os
import re
import time
import shutil
from pathlib import Path

import lib.color as color
from lib.path import list_sorted_dirs, list_sorted_files, list_sorted_daf
from lib.extract import extract_single_file
from lib.pattern import NAME_SPLIT_PATTERN, STUDENT_ID_NAME_PATTERN
from lib.choose import select_from_list



# project
dirs = list_sorted_dirs("./")
dirs = [i for i in dirs if i not in ["tmp", "lib", ".git", ".vscode", ".idea"]]
dirs.sort()
color.print(f"choose the project: ", color.blue)
project_name = select_from_list(dirs)
color.print(f"\nchoosen: {project_name}", color.green)


# input files
flag = "dir"
project_file = Path(f"./{project_name}/submissions/")
project_zip_file = Path(f"./{project_name}/submissions.zip")
# files to generate / write
extract_dir = Path(f"./{project_name}/extract/")
error_output = Path(f"./{project_name}/error.txt")


# no file
if not os.path.exists(project_file) or not os.path.isdir(project_file):
    flag = "zip"
    if not os.path.exists(project_zip_file) or not os.path.isfile(project_zip_file):
        flag = "error"
        raise ValueError(f"no directory called {project_file}")

if flag == "zip":
    color.print(f"extract {project_zip_file} to {project_file}", color.blue)
    if not os.path.exists(project_file):
        project_file.mkdir(parents=True, exist_ok=True)
    extract_single_file(path="./", zipname=project_zip_file, target_path="./", target_dir=project_file)

# get all files in <project_file>
color.print(f"use {project_file}/", color.blue)
color.print(f"{extract_dir} and {error_output} will be overwrite (deleted), please be careful!", color.yellow)
all_files = list_sorted_files(project_file)


# delete old files
shutil.rmtree(extract_dir, ignore_errors=True)
extract_dir.mkdir(parents=True, exist_ok=True)
if os.path.exists(error_output): os.remove(error_output)


# not used
not_used_dirs_or_files = [".git", ".vscode", ".idea", "__pycache__", "__MACOSX", "Thumbs.db", ".DS_Store"]


# extract all
error_list = []
num = 0
for filename in all_files:
    num += 1

    # extract all .zip, .rar, .7z files in <project_file>
    # and rename them with the NAME_SPLIT_PATTERN,
    # if error (not .zip, .rar, .7z), put into error_list and continue
    filename = str(filename)
    filename_stem = Path(filename).stem
    try:
        res = NAME_SPLIT_PATTERN.match(filename_stem)
        real_filename = res.group(1)
        res2 = STUDENT_ID_NAME_PATTERN.match(real_filename)
        error_test = res2.group(0)
    except:
        color.print(f"not a valid filename: {color.underline}{project_file / filename}", color.bold + color.red)
        error_list.append(f"[{num}] not a valid filename: {project_file / filename}")
        continue
    color.print_still(f"now {num} ", color.purple)
    if not extract_single_file(
        path=project_file, zipname=filename, target_path=extract_dir, target_dir=real_filename
    ):
        color.print(f"not a zip package: {color.underline}{project_file / filename}", color.bold + color.red)
        error_list.append(f"[{num}] not a zip package: {project_file / filename}")
        continue

    # refactor the file structure in the extracted file

    # > get information inner the extracted file
    data = {"root-compress": None, "compress": None, "dirs": [], "files": []}
    dir_list, file_list = list_sorted_daf(extract_dir / real_filename)

    # > pre-prepare data: remove __MACOSX, .DS_Store, etc.

    for inner_dir in dir_list:
        if inner_dir in not_used_dirs_or_files:
            shutil.rmtree(extract_dir / real_filename / inner_dir)
    for inner_file in file_list:
        if inner_file in not_used_dirs_or_files:
            os.remove(extract_dir / real_filename / inner_file)

    dir_list, file_list = list_sorted_daf(extract_dir / real_filename)

    # > prepare data

    # case (1): prepare to move inner file such as "zhangsan/zhangsan/.../zhangsan/1.py" to outer "zhangsan/1.py" (ignore __MACOSX, etc.)
    if len(dir_list) == 1 and len(file_list) == 0:
        while len(dir_list) == 1 and len(file_list) == 0:
            if data["root-compress"] is None:
                data["root-compress"] = dir_list[0]
                data["compress"] = dir_list[0]
            else:
                data["compress"] = Path(data["compress"]) / dir_list[0]
            dir_list, file_list = list_sorted_daf(extract_dir / real_filename / data["compress"])
            dir_list = [i for i in dir_list if i not in not_used_dirs_or_files]
            file_list = [i for i in file_list if i not in not_used_dirs_or_files]
            data["dirs"], data["files"] = dir_list, file_list

    # case (2): if is already "zhangsan/1.py", continue
    else:
        data["dirs"], data["files"] = dir_list, file_list

    # > move and delete files

    # case (1): move inner files, except configs or caches, and delete inner files
    if data["root-compress"] is not None:
        for inner_dir in data["dirs"]:
            if inner_dir not in not_used_dirs_or_files:
                os.replace(
                    extract_dir / real_filename / data["compress"] / inner_dir,
                    extract_dir / real_filename / inner_dir
                )
        for inner_file in data["files"]:
            if inner_file not in not_used_dirs_or_files:
                os.replace(
                    extract_dir / real_filename / data["compress"] / inner_file,
                    extract_dir / real_filename / inner_file
                )
        shutil.rmtree(extract_dir / real_filename / data["root-compress"])

    # case (2): no inner files to move
    else:
        pass

    # > re-check
    dir_contents, file_contents = list_sorted_daf(extract_dir / real_filename)
    if len(file_contents) <= 1 or len(dir_contents) >= 1:
        color.print(f"contents may error: {color.underline}{extract_dir / real_filename}", color.bold + color.red)
        error_list.append(f"[{num}] contents may error: {extract_dir / real_filename}")

    # > haha, show slowly to make it more beautiful :)
    time.sleep(0.01)


# write error_list to file
with open(error_output, "w+") as f:
    for i in error_list:
        f.write(i + "\n")
