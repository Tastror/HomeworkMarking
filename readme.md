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
    zhangsan.zip
        question1.py
        question2.py
    lisi.zip
        question1.py
        question2.py
    wangwu.zip
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

Use

```shell
python extract_all.py
```

to extract zip/rar to `tmp/`.

Resolve the error if has, and use

```shell
python mark_all.py
```

to mark scores. Just follow the prompt, and the result will be saved as an excel file.

In `mark_all.py`, you can stop at any time you want (Ctrl + C), and start from any index you want.
