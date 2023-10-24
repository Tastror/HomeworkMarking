import os
import sys
import time
import shutil
import zipfile
import patoolib
from pathlib import Path


def print_there(x, y, text, color):
    # \033[x;yf or \033[x;yH: move to x, y
    # \0337 or \033[s: save cursor position
    # \0338 or \033[u: restore cursor position
    # \033[xm: change to x color (0 reset, 1 bold, 4 underline, 30~37 90~97 colors)
    # \033[a;b;cm: equal to \033[am\033[bm\033[cm
    sys.stdout.write(f"\0337\033[{x};{y}f\033[{color}m{text}\033[0m\0338")
    sys.stdout.flush()


def print_still(text, color):
    # \033[xA: move up x chars
    # \033[xB: move down x chars
    # \033[xC: move right x chars
    # \033[xD: move left x chars
    sys.stdout.write(f"\033[{len(text)}D\033[{color}m{text}\033[0m")
    sys.stdout.flush()


# download unrar first! such as
# (Arch) sudo pacman -S unrar
# (Ubuntu) sudo apt install unrar
# (Windows) winget install unrar
def extract_single_file(
    path: str, zipname: str, target_path: str, target_dir: str
):
    if zipname.endswith(".zip"):
        (target_path / target_dir).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path / zipname, 'r') as f:
            for file in f.namelist():
                f.extract(file, target_path / target_dir)
        return True
    elif zipname.endswith((".rar", ".7z")):
        (target_path / target_dir).mkdir(parents=True, exist_ok=True)
        patoolib.extract_archive(
            path / zipname, verbosity=-1,
            outdir=target_path / target_dir, interactive=False
        )
        return True
    return False


# define and input
temp = Path("./tmp/")
temp_error = Path("./tmp_error.txt")
print(f"\033[93m{temp} and {temp_error} will be overwrite (deleted), please be careful!\033[0m")
path = Path(input("\033[94mlab name (lab1, lab2, ...): \033[0m"))

# get all files in <path>
print(f"\033[94muse {path}/\033[0m")
if not os.path.exists(path) or not os.path.isdir(path):
    raise ValueError(f"no directory called {path}")
_, _, all_files = tuple(next(os.walk(path)))

# delete old files
shutil.rmtree(temp)
temp.mkdir(parents=True, exist_ok=True)
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
    print_still(f"now {num} ", 94)
    if not extract_single_file(
        path=path, zipname=filename, target_path=temp, target_dir=real_filename
    ):
        print(f"\033[1;91mnot a zip package: \033[4m{path / filename}\033[0m")
        error_list.append(f"[{num}] not a zip package: {path / filename}")
        continue
    
    # (1) move inner file such as "zhangsan/zhangsan/1.py" to outer "zhangsan/1.py"
    # (2) if is already "zhangsan/1.py", continue
    # (3) if is "zhangsan/zhangsan/..." and "zhangsan/__MACOSX/...", remove __MACOSX and do (1) again
    # (4) also, delete .vscode, .idea, __pycache__
    data = {"dirname": None, "dirs": [], "files": []}
    walk_gen = os.walk(temp / real_filename)
    _, dir_list, file_list = next(walk_gen)
    if len(dir_list) == 1 and len(file_list) == 0:  # (1)
        data["dirname"] = dir_list[0]
        _, data["dirs"], data["files"] = next(walk_gen)  # only one dir, so it is safe to use this
    elif len(dir_list) == 2 and "__MACOSX" in dir_list and len(file_list) == 0:  # (3)
        shutil.rmtree(temp / real_filename / "__MACOSX")
        # (3) do (1) here
        data["dirname"] = dir_list[0] if dir_list[1] == "__MACOSX" else dir_list[1]
        _, data["dirs"], data["files"] = next(os.walk(temp / real_filename / data["dirname"]))
    else:  # (2)
        data["dirs"], data["files"] = dir_list, file_list
    
    if data["dirname"] is not None:
        for inner_file in data["dirs"]:  # (4) and (1)
            if inner_file not in [".vscode", ".idea", "__pycache__"]:
                os.replace(
                    temp / real_filename / data["dirname"] / inner_file,
                    temp / real_filename / inner_file
                )
        for inner_file in data["files"]:  # (1)
            os.replace(
                temp / real_filename / data["dirname"] / inner_file,
                temp / real_filename / inner_file
            )
        shutil.rmtree(temp / real_filename / data["dirname"])  # (4) and (1)
    else:
        for inner_file in data["dirs"]:  # (4)
            if inner_file in [".vscode", ".idea", "__pycache__"]:
                shutil.rmtree(temp / real_filename / inner_file)
    
    # recheck
    _, dir_contents, file_contents = next(os.walk(temp / real_filename))
    if len(file_contents) <= 1 or len(dir_contents) >= 1:
        print(f"\033[1;91mcontents may error: \033[4m{temp / real_filename}\033[0m")
        error_list.append(f"[{num}] contents may error: {temp / real_filename}")

    # haha, show slowly to be more beautiful :)
    time.sleep(0.01)

# write error_list to file
with open(temp_error, "w+") as f:
    for i in error_list:
        f.write(i + "\n")
