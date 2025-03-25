import os
import pandas
from copy import deepcopy

class ExcelIO:
    def __init__(self, file: str):
        self._file = file
        self._init = False
        self._single_df = None
        self._df_sheets = None

    def excel_init(self, row_list: list[str], col_list: list[str]) -> None:

        if self._init: return

        self._init = True
        self._df_sheets = {}

        field = {}
        for i in col_list:
            field[i] = []
        self._template_df = pandas.DataFrame(field, dtype=object)
        # init all cols
        for i in row_list:
            self._template_df.at[i, col_list[0]] = ""

    def square_excel_init(self, row_col_list: list[str]) -> None:
        self.excel_init(row_col_list, row_col_list)

    def score_excel_init(self, work_list: list[str]) -> None:

        if self._init: return

        self._init = True
        if os.path.exists(self._file):
            self._single_df = pandas.read_excel(self._file, index_col=0)
            return
    
        cols = ["name", "id", "all_score"]
        for v in work_list:
            cols.extend([v + "_score", v + "_comment"])
        field = {}
        for i in cols:
            field[i] = []
        self._single_df = pandas.DataFrame(field)

    def write(self, row_name, col_name, sheet, data) -> None:
        self._df_sheets.setdefault(sheet, deepcopy(self._template_df))
        self._df_sheets[sheet].at[row_name, col_name] = data

    def score_write(self, name: str, id: int, all_score: str, score_comment_dict: dict[str, list[int, str]]) -> None:
        now_row = self.row_num
        self._single_df.loc[now_row, ['name', 'id', 'all_score']] = [name, id, all_score]
        for k, v in score_comment_dict.items():
            self._single_df.at[now_row, k + "_score"] = v[0]
            self._single_df.at[now_row, k + "_comment"] = v[1]

    def dump(self) -> None:
        if self._single_df is None:
            writer = pandas.ExcelWriter(self._file)
            for k, v in self._df_sheets.items():
                v.to_excel(writer, k)
            writer._save()
        elif self._df_sheets is None:
            self._single_df.to_excel(self._file)
        else:
            raise ValueError("dump error, did not init")

    @property
    def row_num(self) -> int:
        return self._single_df.shape[0]
