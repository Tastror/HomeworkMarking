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
        ignore_case: bool = True,
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
        question_dirs.sort()

        for question_name in question_dirs:
            if self.ignore_case:
                question_name = question_name.lower()
            self.project_testcase_dict[question_name] = {}
            r = self.project_testcase_dict[question_name]  # r is a short alias
            _, _, subtestcase_int_files = next(os.walk(self.project_testcase_dir_path / question_name))
            subtestcase_int_files.sort()
            for subtestcase_int_name in subtestcase_int_files:
                num = Path(subtestcase_int_name).stem
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
        files_to_judge.sort()

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
        try:
            # this won't work well if you don't have code (vscode) command in your PATH
            # while unix is more common to have code (vscode) command
            subprocess.Popen(['code', self.project_input_dir_path / self.next_question_filename], shell=False)
        except FileNotFoundError:
            # this won't work well in unix, while works in windows
            subprocess.Popen(['code', self.project_input_dir_path / self.next_question_filename], shell=True)


    def judge(self, whole_files: bool = False) -> int:

        if not self.judge_usage:
            raise SyntaxError("this function can only be used during yield_judge_list() iter time")

        testcase_dict = self.project_testcase_dict[Path(self.next_question_filename).stem]

        shutil.rmtree(self.temp_dir_path, ignore_errors=True)
        self.temp_dir_path.mkdir(parents=True, exist_ok=True)
        if whole_files:
            _, _, filenames = next(os.walk(self.project_input_dir_path))
            filenames.sort()
            for i in filenames:
                shutil.copyfile(self.project_input_dir_path / i, self.temp_dir_path / i)
        else:
            shutil.copyfile(self.project_input_dir_path / self.next_question_filename, self.temp_dir_path / self.next_question_filename)

        def get_rid_of_dangerous_code(file_path):
            with open(file_path, errors='ignore') as f:
                s = f.read()
                dangerous = [" os", " sys", " shutil", " pathlib", " subprocess"]
                flag = False
                for i in dangerous:
                    if i in s:
                        flag = True
                        break
                if flag:
                    color.print("This code may be dangerous! Showing in vscode", color.red)
                    self.show_in_vscode()
                    while True:
                        ready = color.input("ready to run? input 'ready' to continue, 'abort' to abort: ", color.red)
                        if ready == "abort":
                            color.print("abort")
                            return 0
                        elif ready == "ready":
                            color.print("continue")
                            shutil.copyfile(self.project_input_dir_path / self.next_question_filename, self.temp_dir_path / self.next_question_filename)
                            break

        if whole_files:
            for i in filenames:
                get_rid_of_dangerous_code(self.temp_dir_path / i)
        else:
            get_rid_of_dangerous_code(self.temp_dir_path / self.next_question_filename)

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
        # p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        try:
            output, _ = p.communicate(input=bytes(testcase_data["in"], encoding='utf-8'), timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            o = "Time Limit Exceeded"
        else:
            o = str(output, encoding='utf-8').strip().replace('\r', '')
        right_answer = testcase_data["out"].strip().replace('\r', '')
        input_data = testcase_data["in"].strip().replace('\r', '')

        # show output
        color.print("given input:", color.cyan)
        color.print(input_data)
        color.print("its output:", color.cyan)
        color.print(o)
        color.print("right output:", color.cyan)
        color.print(right_answer, color.green)

        if right_answer == o:
            color.print("TOTAL RIGHT", color.green)
            return True
        elif right_answer in o:
            color.print("CONTAIN RIGHT", color.yellow)
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
        # p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p = subprocess.Popen(['python', file_to_judge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        try:
            output, error = p.communicate(input=bytes("0\n" * 10, encoding='utf-8'), timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            o = "Time Limit Exceeded"
            e = "Time Limit Exceeded"
        else:
            o = str(output, encoding='utf-8').strip('\n')
            e = str(error, encoding='utf-8').strip('\n')

        if len(e) > 0:
            color.print("its error:", color.cyan)
            color.print(e)
            color.print("its output:", color.cyan)
            color.print(o)
            color.print("WRONG", color.red)
            return False
        else:
            color.print("RIGHT", color.green)
            return True
