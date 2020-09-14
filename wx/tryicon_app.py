# based on:
# - https://stackoverflow.com/questions/6389580/quick-and-easy-trayicon-with-python
# - https://www.blog.pythonlibrary.org/2013/07/12/wxpython-how-to-minimize-to-system-tray/
import wx
import wx.adv

TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'icon.png'

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.icon = wx.Icon(TRAY_ICON)
        self.SetIcon(self.icon, TRAY_TOOLTIP)
        print(self.IsOk())
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def on_left_down(self, event):
        # self.show_ballon('Tray icon was left-clicked.')
        self.frame.Show()
        self.frame.Restore()

    def on_hello(self, event):
        self.show_ballon('Hello, world!')

    def on_exit(self, event):
        # wx.CallAfter(self.Destroy)
        self.frame.Close()

    def show_ballon(self, message):
        title = "My App"
        self.ShowBalloon(title, message)

class MainFrame(wx.Frame):
    def __init__(self):
        super(wx.Frame, self).__init__(None, title="Minimize to Tray")
        self.tb_icon = TaskBarIcon(self)
        self.tb_icon.CreatePopupMenu()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ICONIZE, self.on_minimize)

    def on_close(self, event):
        self.tb_icon.RemoveIcon()
        self.tb_icon.Destroy()
        self.Destroy()

    def on_minimize(self, event):
        if self.IsIconized():
            self.Hide()

class App(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
