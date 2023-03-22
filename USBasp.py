
import usb.core
import usb.util
import time


VID = 0x16c0
PID = 0x5dc

#USB function call identifiers
USBASP_CONNECT         =   1
USBASP_DISCONNECT      =   2
USBASP_TRANSMIT        =   3
USBASP_READFLASH       =   4
USBASP_ENABLEPROG      =   5
USBASP_WRITEFLASH      =   6
USBASP_READEEPROM      =   7
USBASP_WRITEEEPROM     =   8
USBASP_SETLONGADDRESS  =   9
USBASP_SETISPSCK       =   10
USBASP_TPI_CONNECT     =   11
USBASP_TPI_DISCONNECT  =   12
USBASP_TPI_RAWREAD     =   13
USBASP_TPI_RAWWRITE    =   14
USBASP_TPI_READBLOCK   =   15
USBASP_TPI_WRITEBLOCK  =   16
USBASP_GETCAPABILITIES =   127


def USBtransmit(Request, Byte1, Byte2, Byte3, Byte4):
    ret = dev.ctrl_transfer(0xC0,
                      Request,
                      ((Byte2 & 0xFF) << 0x8) | (Byte1 & 0xFF),
                      ((Byte4 & 0xFF) << 0x8) | (Byte3 & 0xFF),
                      4)
    return(ret)

def Connect():
    global dev
    # Find the USBasp device
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    # Set the active configuration
    dev.set_configuration()
    # Claim the interface
    usb.util.claim_interface(dev, 0)
    USBtransmit(USBASP_CONNECT, 0x00, 0x00, 0x00, 0x00)
    USBtransmit(USBASP_ENABLEPROG, 0x00, 0x00, 0x00, 0x00)

def Disconnect():
    USBtransmit(USBASP_DISCONNECT, 0x00, 0x00, 0x00, 0x00)
    # Release the interface
    usb.util.release_interface(dev, 0)

def Errase():
    # Erase the memory of the microcontroller
    USBtransmit(USBASP_TRANSMIT, 0xAC, 0x80, 0x00, 0x00)

def Write_Flash(flash, flash_page_size):
    global load_percentage
    lenght = 0
    for page in flash:
        lenght = lenght + len(page)
    k = 0
    time.sleep(0.01)
    for i, page in enumerate(flash):
        for j, word in enumerate(page):
            USBtransmit(USBASP_TRANSMIT, 0x40, 0x00, (j)&0xFF, word[0]&0xFF)
            time.sleep(0.01)
            USBtransmit(USBASP_TRANSMIT, 0x48, 0x00, (j)&0xFF, word[1]&0xFF)
            time.sleep(0.01)
            k = k + 1
            load_percentage = 100*k/lenght
        USBtransmit(USBASP_TRANSMIT, 0x4C, ((i*flash_page_size)>>8)&0xFF, (i*flash_page_size)&0xFF, 0x00)
        time.sleep(0.1)

def Read_Flash(flash_page_number, flash_page_size):
    Flash = []
    for adress in range(flash_page_number*flash_page_size):
        Flash.append(USBtransmit(USBASP_TRANSMIT, 0x20, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
        Flash.append(USBtransmit(USBASP_TRANSMIT, 0x28, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
    return(Flash)

def Write_EEPROM(eeprom):
    for adress, word in enumerate(eeprom):
        USBtransmit(USBASP_TRANSMIT, 0xC0, (adress>>8)&0xFF, adress&0xFF, word&0xFF)
        time.sleep(0.01)

def Read_EEPROM(eeprom_page_number, eeprom_page_size):
    eeprom = []
    for adress in range(eeprom_page_number*eeprom_page_size):
        eeprom.append(USBtransmit(USBASP_TRANSMIT, 0xA0, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
    return(eeprom)

def Read_Lock_bits():
    return (USBtransmit(USBASP_TRANSMIT, 0x58, 0x00, 0x00, 0x00)[3])

def Read_Signature_byte():
    a = []
    a.append(USBtransmit(USBASP_TRANSMIT, 0x30, 0x00, 0x00, 0x00)[3])
    a.append(USBtransmit(USBASP_TRANSMIT, 0x30, 0x00, 0x01, 0x00)[3])
    a.append(USBtransmit(USBASP_TRANSMIT, 0x30, 0x00, 0x02, 0x00)[3])
    a.append(USBtransmit(USBASP_TRANSMIT, 0x30, 0x00, 0x03, 0x00)[3])
    a.append(USBtransmit(USBASP_TRANSMIT, 0x30, 0x00, 0x04, 0x00)[3])
    return(a)

def Read_Fuse_bits():
    return (USBtransmit(USBASP_TRANSMIT, 0x50, 0x00, 0x00, 0x00)[3])

def Read_Fuse_high_bits():
    return (USBtransmit(USBASP_TRANSMIT, 0x58, 0x08, 0x00, 0x00)[3])

def Read_extended_Fuse_bits():
    return (USBtransmit(USBASP_TRANSMIT, 0x50, 0x08, 0x00, 0x00)[3])

def Read_calibration_byte():
    return (USBtransmit(USBASP_TRANSMIT, 0x38, 0x00, 0x00, 0x00)[3])
