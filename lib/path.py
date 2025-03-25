import os
from pathlib import Path

def very_stem(file_path) -> str:
    """
    return the very stem of a file path

    e.g. `very_stem("a/b/c.txt.py.a")` -> `"c"`
    """
    very_stem = Path(file_path).stem
    while "." in very_stem:
        very_stem = Path(very_stem).stem
    return very_stem

def list_sorted_daf(path) -> tuple[list[str], list[str]]:
    """short for `list_sorted_dirs_and_files`

    name only (no preceding path)
    
    return (dirs_list, files_list)
    """
    _, all_dirs, all_files = next(os.walk(path))
    all_dirs.sort()
    all_files.sort()
    return all_dirs, all_files

def list_sorted_dirs(path) -> list[str]:
    """
    name only (no preceding path)
    """
    _, all_dirs, _ = next(os.walk(path))
    all_dirs.sort()
    return all_dirs

def list_sorted_files(path) -> list[str]:
    """
    name only (no preceding path)
    """
    _, _, all_files = next(os.walk(path))
    all_files.sort()
    return all_files
