# Homework Marking

A python code to judge and mark python homework automatically.

## Requirements

- Python >= 3.10
- VSCode

install python requirements by yourself :]

## Usage

Create 2 directories, like

```plaintext
homework1/
    123zhangsan_useless_suffix.zip
        question1.py
        question2.py
    456lisi_456_LISI.zip
        question1.py
        question2.py
    789wangwu_wangwu-789-homework1.zip
        question1.py
        question2.py

homework1-testcase/
    question1/
        1.in
        1.out
        2.in
        2.out
    question2/
        1.py  # inner data: assert(Func(1) == 2)
        2.py  # inner data: assert(Func(2) == 3)
```

to prepare for the marking.

Use

```shell
python extract_all.py
```

to extract `.zip/.rar` to `tmp/homework1-extract`. As shown above, the name of the `.zip/.rar` file must be `<id><name>_<any other suffix>`, or you can modify the name split rule in `extract_all.py`.

Some students' zip files may contain invalid contents. To resolve the potential error if has, see `tmp/homework1-error` for more information.

After resolving the errors, use

```shell
python mark_all.py
```

to mark scores. Just follow the prompt, and the result will be saved as an excel file `homework1-result.xlsx`.

Moreover, In `mark_all.py`, you can stop at any time you want (Ctrl + C), and start from any index you want. The result data of students will only be saved at the end of each index's process (prompt is `OK? or Retry? (Enter OK / AnyString Retry):`).

## Testcase

`.in` and `.out` are like

```plaintext
1
2
3
```

```plaintext
6
```

which will just be the input and output of students' .py files. Judging code will detect whether the output is the same (or other detect way, see `JudgeProject.__judge_text()` code in `lib/judge.py`).

`.py` is like

```python
print(getPrimeNum(3))
assert(getPrimeNum(3) == 5)
```

which will append to students' .py files and running. Judging code only fails when exception occurred (which means `assert()` failed here), and it will output both the exception (in stderr) and the normal output (in stdout).
