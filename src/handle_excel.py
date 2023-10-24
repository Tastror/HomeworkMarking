import pandas

class ExcelIO:
    def __init__(self, file: str):
        self._file = file
        self._now = 0

    def excelInit(self, field: dict[str: str | list[int, str]], expect_len: int) -> None:
            for v in field.values():
                v = [pandas.NaN] * expect_len
            self.df = pandas.DataFrame(field)

    def score_excel_init(self, work_list: list[str], expect_len: int) -> None:
            cols = ["name", "id", "all_score"]
            for v in work_list:
                cols.extend([v + "_score", v + "_comment"])
            field = {}
            for i in cols:
                field[i] = [pandas.NA] * expect_len
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
        self._df.loc[self._now, ["name", "id", "all_score"]] = [name, id, all_score]
        for k, v in score_comment_dict.items():
            self._df.at[self._now, k + "_score"] = v[0]
            self._df.at[self._now, k + "_comment"] = v[1]
        self._now += 1

    def append(self, group: list) -> None:
        self._df.append(group)

    def dump(self) -> None:
        self._df.to_excel(self._file)   
