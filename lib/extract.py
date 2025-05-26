import zipfile
import patoolib
from pathlib import Path

# download unrar first! such as
# (Arch) sudo pacman -S unrar
# (Ubuntu) sudo apt install unrar
# (Windows) winget install unrar
# Windows 7z: https://www.7-zip.org/
def extract_single_file(
    path: str | Path, zipname: str | Path, target_path: str | Path, target_dir: str | Path
):
    if str(zipname).endswith(".zip"):
        (Path(target_path) / target_dir).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(Path(path) / zipname, 'r') as f:
            for file in f.namelist():
                f.extract(file, Path(target_path) / target_dir)
        return True
    elif str(zipname).endswith((".rar", ".7z")):
        (Path(target_path) / target_dir).mkdir(parents=True, exist_ok=True)
        patoolib.extract_archive(
            str(Path(path) / zipname), verbosity=-1,
            outdir=str(Path(target_path) / target_dir), interactive=False
        )
        return True
    return False
