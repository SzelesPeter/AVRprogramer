
from intelhex import IntelHex
from arduinobootloader import ArduinoBootloader



ih = IntelHex()
ab = ArduinoBootloader()
prg = ab.select_programmer("Stk500v1")

if prg.open(speed=115200):

    prg.board_request()
    prg.cpu_signature()
    print("botloader name: {} version: {} hardware: {}".format(ab.programmer_name,
                                                               ab.sw_version,
                                                               ab.hw_version))
    print("cpu name: {}".format(ab.cpu_name))
    read_buffer = prg.read_memory(0, 64)
    print(read_buffer)

    prg.leave_bootloader()

else:
    print('nop')
