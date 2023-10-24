from handle_excel import ExcelIO
from mainWindow import ScoringWindow

def test_excel():
    excel_cur = ExcelIO('/testopt/tst.xlsx')
    excel_cur.excelInit({
        '学号': [123, 456],
        '分数': [10, 80],
        '建议': ['no', 'hhh']
    })
    
    excel_cur.append([789, 90, 'yeah'])
    excel_cur.dump()

def test_wind():
    def callback():
        return {
            'text_left': '左边',
            'text_right': '右边',
            'text_bottom': '下面',
            'text_top': '上面'
        }
    
    wd = ScoringWindow(callback)
    wd.run()
    
if __name__ == '__main__':
    test_excel()
    test_wind()