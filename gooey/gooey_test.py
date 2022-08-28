import signal

from gooey import Gooey, GooeyParser
import wx


def parse_args():
    prog_descrip = 'Elapsed / Remaining Timer on Progress in Gooey'
    parser = GooeyParser(description=prog_descrip)
    sub_parsers = parser.add_subparsers(help='commands', dest='command')
    range_parser = sub_parsers.add_parser('range')
    range_parser.add_argument('--length',default=10)
    return parser.parse_args()

def compute_range(length):
    for i in range(length):
        print("someting")
        import time
        from random import randint
        time.sleep(randint(1,3))
        print(f"progress: {i}/{length}")

def handler(*args): 
    print("I am called in response to an external signal!")
    raise Exception("Kaboom!")

@Gooey(
    # optional_cols=2,
    # program_name="Elapsed / Remaining Timer on Progress in Gooey",

    # progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
    # progress_expr="current / total * 100",
    # hide_progress_msg=True,

    # timing_options={
    #     'show_time_remaining':True,
    #     'hide_time_remaining_on_complete':True
    # },
    shutdown_signal=signal.CTRL_BREAK_EVENT,
)
def main():
    conf = parse_args()
    signal.signal(signal.SIGBREAK, handler)
    if conf.command == 'range':
        # try:
            compute_range(int(conf.length))
        # except KeyboardInterrupt:
        #     pass
        #     app = wx.App()
        #     wx.MessageBox("moin")
    print("LOL")

if __name__ == '__main__':
    main()
    print("ENDÖÖÖ")