from openpyxl import load_workbook

fn = 'shop.xlsx'
wb = load_workbook(fn)
ws = wb['Покупки']

def pastedata(datalist):
    ws.append(datalist)
    wb.save(fn)
    wb.close()
