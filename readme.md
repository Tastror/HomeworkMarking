# Homework Marking

A python code to judge and mark python homework automatically.

## Requirements

- Python >= 3.10
- VSCode

install python requirements by yourself :]

(patool, pandas, openpyxl, etc.)

## Usage

Create 2 directories, and put the students' codes and testcases in it, like

```plaintext
homework1/
    raw/
        123zhangsan_useless_suffix.zip
            question1.py
            question2.py
        456lisi_456_LISI.zip
            question1.py
            question2.py
        789wangwu_wangwu-789-homework1.zip
            question1.py
            question2.py
    testcase/
        question1/
            1.in
            1.out
            2.in
            2.out
        question2/
            1.py  # inner data: assert(Func(1) == 2)
            2.py  # inner data: assert(Func(2) == 3)
```

to prepare for the extraction and marking.

### Extract

Use

```shell
python extract_all.py
```

to extract `homework1/raw` to `homework1/extract/`.

As shown above, the name of the `.zip/.rar` file must be `<id><name>_<any other suffix>`, or you can modify the name split rule in `extract_all.py`.

Some students' zip files may contain invalid contents. To resolve the potential error, see `homework1/error.txt` for more information.

### Mark

After resolving the errors, use

```shell
python mark_all.py
```

to mark scores. Just follow the prompt, and the result will be saved as an excel file `homework1/result.xlsx`.

Moreover, In `mark_all.py`, you can stop at any time you want (Ctrl + C), and start from any index you want. The result data of students will only be saved at the end of each index's process (prompt is `OK? or Retry? (just enter -> OK / input any string -> Retry):`).

### Differentiate (Duplication Check)

Use

```shell
python diff_all.py
```

to check the codes' duplication rate. If you have some other codes as benchmark to check the student's codes, put them in `more_diff/` dir as below.

```plaintext
more_diff/
    any_name_you_want/
        homework1/
            question1.py
            question2.py
        homework2/
            question1.py
            question2.py
    benchmark_2/
        homework2/
            question2.py
```

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

which will append to students' .py files and running. Judging code only marks it as false when exception occurred (which means `assert()` failed here), and it will output both the exception (in its stderr) and the normal output (in its stdout) to your screen.
