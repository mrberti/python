import wx

GREEN = (0, 255, 0)

class ButtonFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.btn1 = wx.Button(panel, id=wx.ID_OK, label="PASSED")
        self.btn2 = wx.Button(panel, id=wx.ID_ANY, label="FAILED")
        self.btn3 = wx.Button(panel, id=wx.ID_ABORT, label="CANCEL")

        self.btn1.SetBackgroundColour(GREEN)
        self.btn1.SetForegroundColour((255,0,0))

        vbox.Add(self.btn1, 0, wx.EXPAND)
        vbox.Add(self.btn2, 0, wx.EXPAND)
        vbox.Add(self.btn3, 0, wx.EXPAND)

        panel.SetSizer(vbox)


if __name__ == '__main__':
    app = wx.App()
    frm = ButtonFrame(None, title='Hello World 2')
    frm.Show()
    app.MainLoop()
