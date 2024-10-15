#!/usr/bin/env python3

import os
import time
import shutil
from pathlib import Path

import lib.color as color
from lib.extract import extract_single_file


# input
project_name = ""
while project_name == "":
    project_name = color.input(f"input the project name (lab1, homework1, lab2, etc.): ", color.blue)


# input files
project_file = Path(f"./{project_name}/raw/")
# files to generate / write
extract_dir = Path(f"./{project_name}/extract/")
error_output = Path(f"./{project_name}/error.txt")


# no file
if not os.path.exists(project_file) or not os.path.isdir(project_file):
    raise ValueError(f"no directory called {project_file}")


# get all files in <project_file>
color.print(f"use {project_file}/", color.blue)
color.print(f"{extract_dir} and {error_output} will be overwrite (deleted), please be careful!", color.yellow)
_, _, all_files = next(os.walk(project_file))


# delete old files
shutil.rmtree(extract_dir, ignore_errors=True)
extract_dir.mkdir(parents=True, exist_ok=True)
if os.path.exists(error_output): os.remove(error_output)


# extract all
error_list = []
num = 0
for filename in all_files:
    num += 1

    # extract all .zip, .rar, .7z files in <project_file>
    # and rename them with the beginning name (name before '_'),
    #    such as "005214zhangsan_zha-123.zip" --> "005214zhangsan"
    # if error (not .zip, .rar, .7z), put into error_list and continue
    filename = str(filename)
    real_filename = filename.split('_')[0]
    color.print_still(f"now {num} ", color.purple)
    if not extract_single_file(
        path=project_file, zipname=filename, target_path=extract_dir, target_dir=real_filename
    ):
        color.print(f"not a zip package: {color.underline}{project_file / filename}", color.bold + color.red)
        error_list.append(f"[{num}] not a zip package: {project_file / filename}")
        continue

    # refactor the file structure in the extracted file

    # > get information inner the extracted file
    data = {"dirname": None, "dirs": [], "files": []}
    walk_gen = os.walk(extract_dir / real_filename)
    _, dir_list, file_list = next(walk_gen)

    # > prepare data

    # case (1): prepare to move inner file such as "zhangsan/zhangsan/1.py" to outer "zhangsan/1.py"
    if len(dir_list) == 1 and len(file_list) == 0:
        data["dirname"] = dir_list[0]
        _, data["dirs"], data["files"] = next(walk_gen)  # only one dir, so it is safe to use this

    # case (2): if is "zhangsan/zhangsan/..." and "zhangsan/__MACOSX/...", remove __MACOSX and then do (1)
    elif len(dir_list) == 2 and "__MACOSX" in dir_list and len(file_list) == 0:
        shutil.rmtree(extract_dir / real_filename / "__MACOSX")
        data["dirname"] = dir_list[0] if dir_list[1] == "__MACOSX" else dir_list[1]
        _, data["dirs"], data["files"] = next(os.walk(extract_dir / real_filename / data["dirname"]))

    # case (3): if is already "zhangsan/1.py", continue
    else:
        data["dirs"], data["files"] = dir_list, file_list

    # > move and delete files

    # case [1]: move inner files, except configs or caches, and delete inner files
    if data["dirname"] is not None:
        for inner_file in data["dirs"]:
            if inner_file not in [".vscode", ".idea", "__pycache__", "__MACOSX"]:
                os.replace(
                    extract_dir / real_filename / data["dirname"] / inner_file,
                    extract_dir / real_filename / inner_file
                )
        for inner_file in data["files"]:
            os.replace(
                extract_dir / real_filename / data["dirname"] / inner_file,
                extract_dir / real_filename / inner_file
            )
        shutil.rmtree(extract_dir / real_filename / data["dirname"])

    # case [2]: no inner file to move, just delete configs or caches
    else:
        for inner_file in data["dirs"]:
            if inner_file in [".vscode", ".idea", "__pycache__", "__MACOSX"]:
                shutil.rmtree(extract_dir / real_filename / inner_file)

    # > re-check
    _, dir_contents, file_contents = next(os.walk(extract_dir / real_filename))
    if len(file_contents) <= 1 or len(dir_contents) >= 1:
        color.print(f"contents may error: {color.underline}{extract_dir / real_filename}", color.bold + color.red)
        error_list.append(f"[{num}] contents may error: {extract_dir / real_filename}")

    # > haha, show slowly to bWe more beautiful :)
    time.sleep(0.01)


# write error_list to file
with open(error_output, "w+") as f:
    for i in error_list:
        f.write(i + "\n")
