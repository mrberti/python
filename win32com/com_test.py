#%%
import win32com.client as w32

com_str = "Python.MyComServer"
c = w32.Dispatch(com_str)
print(c.get_data())
# client = w32.GetActiveObject(com_str)
# excel.Visible = True
# excel.Workbooks.Add()
# ws = excel.Worksheets[0]
# ws.Cells(1,1).Value = "123"