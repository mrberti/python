set ampy=python3 -m ampy.cli -p COM3 -b 115200

copy main_433.py main.py
%ampy% put main.py
@REM %ampy% ls
%ampy% reset