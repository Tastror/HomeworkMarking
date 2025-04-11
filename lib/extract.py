import zipfile
import patoolib

# download unrar first! such as
# (Arch) sudo pacman -S unrar
# (Ubuntu) sudo apt install unrar
# (Windows) winget install unrar
# Windows 7z: https://www.7-zip.org/
def extract_single_file(
    path: str, zipname: str, target_path: str, target_dir: str
):
    if str(zipname).endswith(".zip"):
        (target_path / target_dir).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path / zipname, 'r') as f:
            for file in f.namelist():
                f.extract(file, target_path / target_dir)
        return True
    elif str(zipname).endswith((".rar", ".7z")):
        (target_path / target_dir).mkdir(parents=True, exist_ok=True)
        patoolib.extract_archive(
            path / zipname, verbosity=-1,
            outdir=target_path / target_dir, interactive=False
        )
        return True
    return False
