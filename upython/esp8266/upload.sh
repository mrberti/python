connect serial com9
# cp mpu6050.py /pyboard
cp main.py /pyboard
cp wemos.py /pyboard
#repl ~ import mpu6050 ~ 
#repl ~ import machine ~ machine.reset() ~
# repl ~ from wemos import udp_send ~ udp_send("moin", 192.168.1.41, 123) ~
repl