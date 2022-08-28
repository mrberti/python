import wx

app = wx.App()
# print(wx.MessageBox("Hello", style=wx.YES|wx.NO|wx.ICON_ASTERISK))
dlg = wx.TextEntryDialog(None, "asd")
data = dlg.Show(True)
app.MainLoop()
print(data)