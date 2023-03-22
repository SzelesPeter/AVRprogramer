"""
import usb.core
import usb.util

VID = 0x1781
PID = 0x0c9f

# Generic requests to the USBtiny
USBTINY_ECHO    =   0       # echo test
USBTINY_READ    =   1	    # read byte (wIndex:address)
USBTINY_WRITE   =   2	    # write byte (wIndex:address, wValue:value)
USBTINY_CLR     =   3	    # clear bit (wIndex:address, wValue:bitno)
USBTINY_SET     =   4	    # set bit (wIndex:address, wValue:bitno)

# Programming requests
USBTINY_POWERUP      =  5	    # apply power (wValue:SCK-period, wIndex:RESET)
USBTINY_POWERDOWN    =  6	    # remove power from chip
USBTINY_SPI          =  7	    # issue SPI command (wValue:c1c0, wIndex:c3c2)
USBTINY_POLL_BYTES   =  8	    # set poll bytes for write (wValue:p1p2)
USBTINY_FLASH_READ   =  9	    # read flash (wIndex:address)
USBTINY_FLASH_WRITE  =  10	    # write flash (wIndex:address, wValue:timeout)
USBTINY_EEPROM_READ  =  11	    # read eeprom (wIndex:address)
USBTINY_EEPROM_WRITE =  12	    # write eeprom (wIndex:address, wValue:timeout)


def USBtransmit(Request, Byte1, Byte2, Byte3, Byte4):
    dev.ctrl_transfer(bmRequestType=0x40,
                      bRequest=Request,
                      wValue=((Byte2 & 0xFF) << 0x8) | (Byte1 & 0xFF),
                      wIndex=((Byte4 & 0xFF) << 0x8) | (Byte3 & 0xFF))

def Connect():
    global dev
    # Find the USBtinyISP device
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    # Set the active configuration
    dev.set_configuration()
    # Claim the interface
    usb.util.claim_interface(dev, 0)
    USBtransmit(USBTINY_POWERUP, 0x00, 0x00, 0x00, 0x00)
    USBtransmit(USBTINY_SPI, 0xAC, 0x53, 0x00, 0x00)

def Disconnect():
    USBtransmit(USBTINY_POWERDOWN, 0x00, 0x00, 0x00, 0x00)
    # Release the interface
    usb.util.release_interface(dev, 0)

def Errase():
    # Erase the memory of the microcontroller
    USBtransmit(USBTINY_SPI, 0xAC, 0x80, 0x00, 0x00)
"""

#=======================================================================================================================



import usb.core
import usb.util
import time


VID = 0x1781
PID = 0x0c9f

# Generic requests to the USBtiny
USBTINY_ECHO    =   0       # echo test
USBTINY_READ    =   1	    # read byte (wIndex:address)
USBTINY_WRITE   =   2	    # write byte (wIndex:address, wValue:value)
USBTINY_CLR     =   3	    # clear bit (wIndex:address, wValue:bitno)
USBTINY_SET     =   4	    # set bit (wIndex:address, wValue:bitno)

# Programming requests
USBTINY_POWERUP      =  5	    # apply power (wValue:SCK-period, wIndex:RESET)
USBTINY_POWERDOWN    =  6	    # remove power from chip
USBTINY_SPI          =  7	    # issue SPI command (wValue:c1c0, wIndex:c3c2)
USBTINY_POLL_BYTES   =  8	    # set poll bytes for write (wValue:p1p2)
USBTINY_FLASH_READ   =  9	    # read flash (wIndex:address)
USBTINY_FLASH_WRITE  =  10	    # write flash (wIndex:address, wValue:timeout)
USBTINY_EEPROM_READ  =  11	    # read eeprom (wIndex:address)
USBTINY_EEPROM_WRITE =  12	    # write eeprom (wIndex:address, wValue:timeout)



def USBtransmit(Request, Byte1, Byte2, Byte3, Byte4):
    ret = dev.ctrl_transfer(0xC0,
                      Request,
                      ((Byte2 & 0xFF) << 0x8) | (Byte1 & 0xFF),
                      ((Byte4 & 0xFF) << 0x8) | (Byte3 & 0xFF),
                      4)
    return(ret)

def Connect():
    global dev
    # Find the USBtinyISP device
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    # Set the active configuration
    dev.set_configuration()
    # Claim the interface
    usb.util.claim_interface(dev, 0)
    USBtransmit(USBTINY_POWERUP, 0x00, 0x00, 0x00, 0x00)
    USBtransmit(USBTINY_SPI, 0xAC, 0x53, 0x00, 0x00)

def Disconnect():
    USBtransmit(USBTINY_POWERDOWN, 0x00, 0x00, 0x00, 0x00)
    # Release the interface
    usb.util.release_interface(dev, 0)

def Errase():
    # Erase the memory of the microcontroller
    USBtransmit(USBTINY_SPI, 0xAC, 0x80, 0x00, 0x00)

def Write_Flash(flash, flash_page_size):
    global load_percentage
    lenght = 0
    for page in flash:
        lenght = lenght + len(page)
    k = 0
    time.sleep(0.01)
    for i, page in enumerate(flash):
        for j, word in enumerate(page):
            USBtransmit(USBTINY_SPI, 0x40, 0x00, (j)&0xFF, word[0]&0xFF)
            time.sleep(0.01)
            USBtransmit(USBTINY_SPI, 0x48, 0x00, (j)&0xFF, word[1]&0xFF)
            time.sleep(0.01)
            k = k + 1
            load_percentage = 100*k/lenght
        USBtransmit(USBTINY_SPI, 0x4C, ((i*flash_page_size)>>8)&0xFF, (i*flash_page_size)&0xFF, 0x00)
        time.sleep(0.1)

def Read_Flash(flash_page_number, flash_page_size):
    Flash = []
    for adress in range(flash_page_number*flash_page_size):
        Flash.append(USBtransmit(USBTINY_SPI, 0x20, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
        Flash.append(USBtransmit(USBTINY_SPI, 0x28, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
    return(Flash)

def Write_EEPROM(eeprom):
    for adress, word in enumerate(eeprom):
        USBtransmit(USBTINY_SPI, 0xC0, (adress>>8)&0xFF, adress&0xFF, word&0xFF)

def Read_EEPROM(eeprom_page_number, eeprom_page_size):
    eeprom = []
    for adress in range(eeprom_page_number*eeprom_page_size):
        eeprom.append(USBtransmit(USBTINY_SPI, 0xA0, (adress>>8)&0xFF, adress&0xFF, 0x00)[3])
    return(eeprom)

def Read_Lock_bits():
    return (USBtransmit(USBTINY_SPI, 0x58, 0x00, 0x00, 0x00)[3])

def Read_Signature_byte():
    a = []
    a.append(USBtransmit(USBTINY_SPI, 0x30, 0x00, 0x00, 0x00)[3])
    a.append(USBtransmit(USBTINY_SPI, 0x30, 0x00, 0x01, 0x00)[3])
    a.append(USBtransmit(USBTINY_SPI, 0x30, 0x00, 0x02, 0x00)[3])
    a.append(USBtransmit(USBTINY_SPI, 0x30, 0x00, 0x03, 0x00)[3])
    a.append(USBtransmit(USBTINY_SPI, 0x30, 0x00, 0x04, 0x00)[3])
    return(a)

def Read_Fuse_bits():
    return (USBtransmit(USBTINY_SPI, 0x50, 0x00, 0x00, 0x00)[3])

def Read_Fuse_high_bits():
    return (USBtransmit(USBTINY_SPI, 0x58, 0x08, 0x00, 0x00)[3])

def Read_extended_Fuse_bits():
    return (USBtransmit(USBTINY_SPI, 0x50, 0x08, 0x00, 0x00)[3])

def Read_calibration_byte():
    return (USBtransmit(USBTINY_SPI, 0x38, 0x00, 0x00, 0x00)[3])