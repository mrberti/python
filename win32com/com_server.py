import time
import os
import win32com.server.register

GUID = "{BDB5F34F-4764-464A-BD8F-3B8F5D7E7335}"

class MyComServer(object):
    _reg_clsid_ = GUID
    _reg_desc_ = "Python Test COM Server"
    _reg_progid_ = "Python.MyComServer"

    _public_methods_ = ['get_data', 'set_data']
    _public_attrs_ = ['val']
    _readonly_attrs_ = ['instances']

    instances = 0

    def __init__(self):
        # with open("test.log", "a") as f:
        #     f.write(time.time())
        print("INIT CALLED")
        par1 = None
        MyComServer.instances += 1
        self._par1 = par1
        self.val = 1
        print("INIT FINISHED")

    def get_data(self):
        # with open("test.log", "a") as f:
        #     f.write("{} get_data".format(time.time()))
        ret = os.getcwd()
        ret = 123
        return ret
    
    def set_data(self, value):
        self._par1 = value

if __name__ == "__main__":
    win32com.server.register.UseCommandLine(MyComServer)
    # while True:
    #     time.sleep(1)
    #     print(".", end="")