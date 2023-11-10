# Homework Marking

A little python code to judge and mark homework automatically

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

and use 
