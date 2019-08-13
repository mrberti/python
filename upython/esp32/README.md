# NodeMCU-32S
[Pin Outs](https://www.shenzhen2u.com/NodeMCU-32S)

## Flashing
```
esptool.exe --chip esp32 --port COM9 erase_flash
esptool.exe --chip esp32 --port COM9 --baud 460800 write_flash -z 0x1000 <firmware_file>
```