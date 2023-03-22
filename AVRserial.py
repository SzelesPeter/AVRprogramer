
import serial
import time


def AVR_Connect(port):
    global ser
    ser = serial.Serial(port, baudrate=57600, timeout=1)
    time.sleep(1)
    ser.write(b'\x02')
    print(ser.read())
    time.sleep(1)
    ser.write(b'\xAC' + b'\x53' + b'\x00' + b'\x00')

def AVR_Disconnect():
    global ser
    ser.write(b'\xff')
    print(ser.read())
    ser.close()

def AVR_Errase():
    global ser
    time.sleep(0.5)
    ser.write(b'\xAC' + b'\x80' + b'\x00' + b'\x00')
    time.sleep(0.5)

def Write_Flash(flash, flash_page_size):
    global load_percentage
    lenght = 0
    for page in flash:
        lenght = lenght + len(page)
    k = 0
    time.sleep(0.1)
    for i, page in enumerate(flash):
        for j, word in enumerate(page):
            ser.write(b'\x40' + b'\x00' + ((j)&0xFF).to_bytes(1, byteorder='big') + (word[0]&0xFF).to_bytes(1, byteorder='big'))
            time.sleep(0.01)
            ser.write(b'\x48' + b'\x00' + ((j)&0xFF).to_bytes(1, byteorder='big') + (word[1]&0xFF).to_bytes(1, byteorder='big'))
            time.sleep(0.01)
            k = k + 1
            load_percentage = 100*k/lenght
        ser.write(b'\x4C' + (((i*flash_page_size)>>8)&0xFF).to_bytes(1, byteorder='big') + ((i*flash_page_size)&0xFF).to_bytes(1, byteorder='big') + b'\x00')
        time.sleep(0.1)

def Read_Flash(flash_page_number, flash_page_size):
    Flash = []
    time.sleep(0.01)
    for adress in range(flash_page_number*flash_page_size):
        ser.write(b'\x20' + ((adress >> 8) & 0xFF).to_bytes(1, byteorder='big') + (adress & 0xFF).to_bytes(1, byteorder='big') + b'\x00')
        time.sleep(0.01)
        Flash.append(int.from_bytes(ser.read(), byteorder='big'))
        time.sleep(0.01)
        ser.write(b'\x28' + ((adress >> 8) & 0xFF).to_bytes(1, byteorder='big') + (adress & 0xFF).to_bytes(1, byteorder='big') + b'\x00')
        time.sleep(0.01)
        Flash.append(int.from_bytes(ser.read(), byteorder='big'))
        time.sleep(0.01)
    return(Flash)

def Write_EEPROM(eeprom):
    for adress, word in enumerate(eeprom):
        ser.write(b'\xC0' + ((adress>>8)&0xFF).to_bytes(1, byteorder='big') + (adress&0xFF).to_bytes(1, byteorder='big') + (word&0xFF).to_bytes(1, byteorder='big'))
        time.sleep(0.01)

def Read_EEPROM(eeprom_page_number, eeprom_page_size):
    eeprom = []
    time.sleep(0.01)
    for adress in range(eeprom_page_number*eeprom_page_size):
        ser.write(b'\xA0' + ((adress>>8)&0xFF).to_bytes(1, byteorder='big') + (adress&0xFF).to_bytes(1, byteorder='big') + b'\x00')
        time.sleep(0.01)
        eeprom.append(int.from_bytes(ser.read(), byteorder='big'))
        time.sleep(0.01)
    return(eeprom)

def Read_Lock_bits():
    time.sleep(0.01)
    ser.write(b'\x58' + b'\x00' + b'\x00' + b'\x00')
    return (int.from_bytes(ser.read(), byteorder='big'))

def Read_Signature_byte():
    a = []
    time.sleep(0.01)
    ser.write(b'\x30' + b'\x00' + b'\x00' + b'\x00')
    a.append(int.from_bytes(ser.read(), byteorder='big'))
    time.sleep(0.01)
    ser.write(b'\x30' + b'\x00' + b'\x01' + b'\x00')
    a.append(int.from_bytes(ser.read(), byteorder='big'))
    time.sleep(0.01)
    ser.write(b'\x30' + b'\x00' + b'\x02' + b'\x00')
    a.append(int.from_bytes(ser.read(), byteorder='big'))
    time.sleep(0.01)
    ser.write(b'\x30' + b'\x00' + b'\x03' + b'\x00')
    a.append(int.from_bytes(ser.read(), byteorder='big'))
    time.sleep(0.01)
    ser.write(b'\x30' + b'\x00' + b'\x04' + b'\x00')
    a.append(int.from_bytes(ser.read(), byteorder='big'))
    return(a)

def Read_Fuse_bits():
    time.sleep(0.01)
    ser.write(b'\x58' + b'\x00' + b'\x00' + b'\x00')
    return (int.from_bytes(ser.read(), byteorder='big'))

def Read_Fuse_high_bits():
    time.sleep(0.01)
    ser.write(b'\x58' + b'\x08' + b'\x00' + b'\x00')
    return (int.from_bytes(ser.read(), byteorder='big'))

def Read_extended_Fuse_bits():
    time.sleep(0.01)
    ser.write(b'\x50' + b'\x08' + b'\x00' + b'\x00')
    return (int.from_bytes(ser.read(), byteorder='big'))

def Read_calibration_byte():
    time.sleep(0.01)
    ser.write(b'\x38' + b'\x00' + b'\x00' + b'\x00')
    return (int.from_bytes(ser.read(), byteorder='big'))


