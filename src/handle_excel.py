import pandas

# {
#    姓名 : [],
#    作业 : []
#    分数 : []
#}
class ExcelIO:
    def __init__(self, file: str, expect_len: int):
        self._file = file
        self._expect_len = expect_len

    def excelInit(self, 
        field: dict[str: str | list[int, str]]
        ) -> None:
            for v in field.values():
                v = [pandas.NaN] * self._expect_len
            self.df = pandas.DataFrame(field)

    def single_write(self, pos: tuple[int, str], info) -> None:
        self.df.at[pos[0], pos[1]] = info

    def group_write(self, idx, infos, axis: int = 0) -> bool:
        match axis:
            case 0 or 1:
                self.df[idx] = info
            case _:
                return False
        return True

    def append(self, group: list) -> None:
        self.df.append(group)

    def dump(self, path: str | None = None, encoding: str = 'utf-8') -> None:
        self.df.to_excel(path if path else self._file, encoding=encoding)    
    