import tkinter as tk

class ScoringWindow:
    def __init__(self, call):
        self.window = tk.Tk()
        self.windowStyleInit()
        self.call = call

    def windowStyleInit(self):
        # 左侧文字
        self.text_left = tk.Label(self.window, text="上方文字")
        self.text_left.pack(side=tk.LEFT)

        # 上方文字
        self.text_top = tk.Label(self.window, text="上方文字")
        self.text_top.pack()

        # 下方文字
        self.text_bottom = tk.Label(self.window, text="下方文字")
        self.text_bottom.pack()

        # 右侧文字
        self.text_right = tk.Label(self.window, text="右侧文字")
        self.text_right.pack(side=tk.RIGHT)

        # 右下角文本框和按钮
        frame_bottom_right = tk.Frame(self.window)
        frame_bottom_right.pack(side=tk.BOTTOM, anchor='se')

        self.entry_bottom = tk.Entry(frame_bottom_right)
        self.entry_bottom.pack(side=tk.RIGHT)

        button = tk.Button(frame_bottom_right, text="提交", command=self.button_clicked)
        button.pack(side=tk.RIGHT)

    def button_clicked(self):
        input_text = self.entry.get()
        self.text_right.config(text="score：" + input_text)
        self.update_text()
        
    def update_text(self):
        texts = self.call()
        self.text_left = texts.get('text_left')
        self.text_right = texts.get('text_right')
        self.text_top = texts.get('text_top')
        self.text_bottom = texts.get('text_bottom')
        
    def run(self):
        self.window.mainloop()


def func():
    # 你的计算，数据处理的代码
    return {
        'text_left': 'left',
        'text_right': 'right',
        'text_bottom': 'bottom',
        'text_top': 'top'
    }

window = ScoringWindow(func)
window.run()
