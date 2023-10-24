import pandas

class ExcelIO:
    def __init__(self, file: str):
        self._file = file

    def excel_init(self, field: dict[str: str | list[int, str]]) -> None:
        self.df = pandas.DataFrame(field)

    def score_excel_init(self, work_list: list[str]) -> None:
        cols = ["name", "id", "all_score"]
        for v in work_list:
            cols.extend([v + "_score", v + "_comment"])
        field = {}
        for i in cols:
            field[i] = []
        self._df = pandas.DataFrame(field)
        print(self._df)

    def single_write(self, pos: tuple[int, str], info) -> None:
        self._df.at[pos[0], pos[1]] = info

    def group_write(self, idx, infos, axis: int = 0) -> bool:
        match axis:
            case 0 | 1:
                self._df[idx] = infos
            case _:
                return False
        return True

    def score_write(self, name: str, id: int, all_score: str, score_comment_dict: dict[str, list[int, str]]) -> None:
        now_row = self._df.shape[0]
        self._df.loc[now_row, ['name', 'id', 'all_score']] = [name, id, all_score]
        for k, v in score_comment_dict.items():
            self._df.at[now_row, k + "_score"] = v[0]
            self._df.at[now_row, k + "_comment"] = v[1]

    def append(self, group: list) -> None:
        self._df._append([group])

    def dump(self) -> None:
        self._df.to_excel(self._file)   
