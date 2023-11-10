import os
import time
import shutil
from pathlib import Path

import lib.color as color
from lib.extract import extract_single_file


# define and input
path = Path(color.input(f"lab name (lab1, lab2, ...): ", color.blue))
temp_extract = Path(f"./tmp/{path}-extract/")
temp_error = Path(f"./tmp/{path}-error.txt")
color.print(f"{temp_extract} and {temp_error} will be overwrite (deleted), please be careful!", color.yellow)


# get all files in <path>
color.print(f"use {path}/", color.blue)
if not os.path.exists(path) or not os.path.isdir(path):
    raise ValueError(f"no directory called {path}")
_, _, all_files = tuple(next(os.walk(path)))


# delete old files
shutil.rmtree(temp_extract, ignore_errors=True)
temp_extract.mkdir(parents=True, exist_ok=True)
if os.path.exists(temp_error): os.remove(temp_error)


# extract all
error_list = []
num = 0
for filename in all_files:
    num += 1

    # extract all .zip, .rar, .7z files in <path>
    # and rename them with the beginning name (name before '_'),
    #    such as "005214zhangsan_zha-123.zip" --> "005214zhangsan"
    # if error (not .zip, .rar, .7z), put into error_list and continue
    filename = str(filename)
    real_filename = filename.split('_')[0]
    color.print_still(f"now {num} ", color.purple)
    if not extract_single_file(
        path=path, zipname=filename, target_path=temp_extract, target_dir=real_filename
    ):
        color.print(f"not a zip package: {color.underline}{path / filename}", color.bold + color.red)
        error_list.append(f"[{num}] not a zip package: {path / filename}")
        continue

    # refactor the file structure in the extracted file

    # > get information inner the extracted file
    data = {"dirname": None, "dirs": [], "files": []}
    walk_gen = os.walk(temp_extract / real_filename)
    _, dir_list, file_list = next(walk_gen)

    # > prepare data

    # case (1): prepare to move inner file such as "zhangsan/zhangsan/1.py" to outer "zhangsan/1.py"
    if len(dir_list) == 1 and len(file_list) == 0:
        data["dirname"] = dir_list[0]
        _, data["dirs"], data["files"] = next(walk_gen)  # only one dir, so it is safe to use this

    # case (2): if is "zhangsan/zhangsan/..." and "zhangsan/__MACOSX/...", remove __MACOSX and then do (1)
    elif len(dir_list) == 2 and "__MACOSX" in dir_list and len(file_list) == 0:
        shutil.rmtree(temp_extract / real_filename / "__MACOSX")
        data["dirname"] = dir_list[0] if dir_list[1] == "__MACOSX" else dir_list[1]
        _, data["dirs"], data["files"] = next(os.walk(temp_extract / real_filename / data["dirname"]))

    # case (3): if is already "zhangsan/1.py", continue
    else:
        data["dirs"], data["files"] = dir_list, file_list

    # > move and delete files

    # case [1]: move inner files, except configs or caches, and delete inner files
    if data["dirname"] is not None:
        for inner_file in data["dirs"]:
            if inner_file not in [".vscode", ".idea", "__pycache__"]:
                os.replace(
                    temp_extract / real_filename / data["dirname"] / inner_file,
                    temp_extract / real_filename / inner_file
                )
        for inner_file in data["files"]:
            os.replace(
                temp_extract / real_filename / data["dirname"] / inner_file,
                temp_extract / real_filename / inner_file
            )
        shutil.rmtree(temp_extract / real_filename / data["dirname"])

    # case [2]: no inner file to move, just delete configs or caches
    else:
        for inner_file in data["dirs"]:
            if inner_file in [".vscode", ".idea", "__pycache__"]:
                shutil.rmtree(temp_extract / real_filename / inner_file)

    # > re-check
    _, dir_contents, file_contents = next(os.walk(temp_extract / real_filename))
    if len(file_contents) <= 1 or len(dir_contents) >= 1:
        color.print(f"contents may error: {color.underline}{temp_extract / real_filename}", color.bold + color.red)
        error_list.append(f"[{num}] contents may error: {temp_extract / real_filename}")

    # > haha, show slowly to bWe more beautiful :)
    time.sleep(0.01)


# write error_list to file
with open(temp_error, "w+") as f:
    for i in error_list:
        f.write(i + "\n")
