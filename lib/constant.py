TEMP_DIR = "tmp"

ROOT_DIR_NOT_READ = [
    TEMP_DIR,
    "lib", "more_diff",
    ".git", ".venv", ".vscode", ".idea", "__pycache__",
    "__MACOSX"
]
DATA_NOT_USED_IN_MARK = [
    ".git", ".venv", ".vscode", ".idea", "__pycache__",
    "__MACOSX", "Thumbs.db", ".DS_Store"
]

# ./xxx_dir
MORE_DIFF_DIR = "more_diff"

# ./labn/xxx-dir,zip
SUBMISSION_DIR = "submissions"
SUBMISSION_ZIP = SUBMISSION_DIR + ".zip"
EXTRACT_DIR = "extract"
TESTCASE_DIR = "testcase"

# ./labn/xxx-file
ERROR_FILE = "error.txt"
RESULT_EXCEL = "result.xlsx"
DIFF_EXCEL = "diff.xlsx"
DIFF_COUNT_EXCEL = "diff-count.xlsx"
