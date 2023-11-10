import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TypedDict, Literal, Optional, Iterator

import lib.color as color

SingleTestcase = TypedDict(
    'SingleTestcase',
    {
        'type': Literal['py', 'text'],
        'py': Optional[str],
        'in': Optional[str],
        'out': Optional[str],
    }
)

class JudgeProject:


    def __init__(
        self,
        project_testcase_dir_path: Path,
        project_input_dir_path: Optional[Path] = None,
        temp_dir_path: Path = Path("./tmp/judge/"),
        ignore_case: bool = True
    ):
        """
        Args:
            project_testcase_dir_path: directory structure is `dir -> name1/{1.in, 1.out, 2.in, 2.out}, name2/{1.py, 2.py}, abc/{1.py, 2.in, 2.out}, ...`
            project_input_dir_path: directory structure is `dir -> name1.py, name2.py, abc.py, ...`
            temp_dir_path: temp directory, you can delete manually after running
            ignore_case: True or False
        """

        self.project_testcase_dir_path = Path(project_testcase_dir_path)
        self.project_input_dir_path = Path(project_input_dir_path) if project_input_dir_path is not None else None
        self.temp_dir_path = Path(temp_dir_path)
        self.ignore_case = ignore_case
        self.judge_usage = False

        self.project_testcase_dict: dict[str, dict[int, SingleTestcase]] = {}
        self.next_question_filename = ""

        _, question_dirs, _ = next(os.walk(self.project_testcase_dir_path))

        for question_name in question_dirs:
            if self.ignore_case:
                question_name = question_name.lower()
            self.project_testcase_dict[question_name] = {}
            r = self.project_testcase_dict[question_name]  # r is a short alias
            _, _, subtestcase_int_files = next(os.walk(self.project_testcase_dir_path / question_name))
            for subtestcase_int_name in subtestcase_int_files:
                num = int(Path(subtestcase_int_name).stem)
                r.setdefault(num, {})
                suffix = Path(subtestcase_int_name).suffix
                if suffix == ".in":
                    r[num]["type"] = "text"
                    with open(self.project_testcase_dir_path / question_name / subtestcase_int_name) as f:
                        r[num]["in"] = f.read() + '\n'
                elif suffix == ".out":
                    r[num]["type"] = "text"
                    with open(self.project_testcase_dir_path / question_name / subtestcase_int_name) as f:
                        r[num]["out"] = f.read()
                elif suffix == ".py":
                    r[num]["type"] = "py"
                    with open(self.project_testcase_dir_path / question_name / subtestcase_int_name) as f:
                        r[num]["py"] = f.read()
                else:
                    raise ValueError(f"cannot recognize suffix {self.project_testcase_dir_path / question_name / subtestcase_int_name}")


    def yield_judge_list(self, project_input_dir_path: Optional[Path] = None) -> Iterator[str]:
        """
        Args:
            project_input_dir_path: directory structure is `dir -> name1.py, name2.py, abc.py, ...`
        Usage:
            ```python
            from judge import JudgeProject
            jp = JudgeProject('./testcase/')
            for question_name in jp.yield_judge_list("./handin/zhangsan/"):
                print("judging", question_name)
                result = jp.judge()
                if result != 100:
                    jp.show_in_vscode()
            ```
        """
        self.judge_usage = True

        if project_input_dir_path is not None:
            self.project_input_dir_path = Path(project_input_dir_path)
        if self.project_input_dir_path is None:
            raise ValueError(f"did not specify project_input_dir_path")

        _, _, files_to_judge = next(os.walk(self.project_input_dir_path))

        for file_to_judge in files_to_judge:
            if self.ignore_case:
                file_to_judge = file_to_judge.lower()
            if self.project_testcase_dict.get(Path(file_to_judge).stem, None) is None:
                color.print(f"skip {self.project_input_dir_path / file_to_judge} since its name does not match any testcase name", color.red)
                continue
            self.next_question_filename = file_to_judge
            yield Path(file_to_judge).stem

        self.judge_usage = False
        return "yield_judge_list() StopIter"


    def show_in_vscode(self):
        if not self.judge_usage:
            raise SyntaxError("this function can only be used during yield_judge_list() iter time")
        subprocess.Popen(['code', self.project_input_dir_path / self.next_question_filename], shell=True)


    def judge(self) -> int:

        if not self.judge_usage:
            raise SyntaxError("this function can only be used during yield_judge_list() iter time")

        shutil.rmtree(self.temp_dir_path, ignore_errors=True)
        self.temp_dir_path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.project_input_dir_path / self.next_question_filename, self.temp_dir_path / self.next_question_filename)
        testcase_dict = self.project_testcase_dict[Path(self.next_question_filename).stem]

        count, right = 0, 0

        for num, testcase_data in testcase_dict.items():
            color.print(f"testing testcase {num}", color.cyan)
            # use for judge function assertion (append .py data to file)
            if testcase_data["type"] == "py":
                if self.__judge_py(num): right += 1
                # refresh file
                shutil.copyfile(self.project_input_dir_path / self.next_question_filename, self.temp_dir_path / self.next_question_filename)
                count += 1
            # use for normal input & output
            elif testcase_data["type"] == "text":
                if self.__judge_text(num): right += 1
                count += 1
            else:
                raise ValueError(f"testcase type error: {testcase_data['type']} in {Path(self.next_question_filename).stem}")

        # get score
        return round(right / count * 50 + 50) if count > 0 else 100


    def __judge_text(self, num: int) -> bool:

        if not self.judge_usage:
            raise SyntaxError("this function can only be used during yield_judge_list() iter time")

        file_to_judge = self.temp_dir_path / self.next_question_filename
        testcase_data = self.project_testcase_dict[Path(self.next_question_filename).stem][num]

        # run and get output; error will print on the screen
        p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        output, _ = p.communicate(input=bytes(testcase_data["in"], encoding='utf-8'))
        o = str(output, encoding='utf-8').strip('\n')

        # show output
        color.print("his/her input phrases and answer:", color.cyan)
        print(o)
        color.print("right answer:", color.cyan)
        print(testcase_data["out"])

        # check if is right (use "in", very loose)
        if testcase_data["out"] in o:
            color.print("RIGHT", color.green)
            return True
        else:
            color.print("WRONG", color.red)
            return False


    def __judge_py(self, num: int) -> bool:

        if not self.judge_usage:
            raise SyntaxError("this function can only be used during yield_judge_list() iter time")

        file_to_judge = self.temp_dir_path / self.next_question_filename
        testcase_data = self.project_testcase_dict[Path(self.next_question_filename).stem][num]

        # append testdata at the end
        with open(file_to_judge, 'a+') as f:
            f.write('\n' + testcase_data["py"])

        # run and get error only (assertion error)
        p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _, error = p.communicate(input=bytes("0\n" * 10, encoding='utf-8'))
        e = str(error, encoding='utf-8').strip('\n')

        if len(e) > 0:
            color.print("wrong point:", color.cyan)
            print(e)
            color.print("WRONG", color.red)
            return False
        else:
            color.print("RIGHT", color.green)
            return True
