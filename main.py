

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import serial
import serial.tools.list_ports
import time
import usb.core
import usb.util
import threading

import USBasp
import USBtinyASP
import AVRserial
from file_kezeles import *
from file_kezeles import *

#================================= PLACEHOLDER =========================================================================
def place_holder():
    pass
placeholder = 0
Load_status = 0
#==================================== Microcontroller data =============================================================
#  name, signature byte 0x000 0x001 0x002, flash page size, flash page number,  eeprom page size,  eeprom page number
AVR_mem_size = [[' ATtiny24A', 0x1E, 0x91, 0x0B, 16, 64, 4, 32],
                [' ATtiny44A', 0x1E, 0x92, 0x07, 32, 64, 4, 64],
                [' ATtiny84A', 0x1E, 0x93, 0x0C, 32, 128, 4, 128],
                [' ATtiny25', 0x1E, 0x91, 0x08, 16, 64, 4, 32],
                [' ATtiny45', 0x1E, 0x92, 0x06, 32, 64, 4, 64],
                [' ATtiny85', 0x1E, 0x93, 0x0B, 32, 128, 4, 128],
                [' ATtiny2313A', 0x1E, 0x91, 0x0A, 16, 64, 4, 32],
                [' ATtiny4313', 0x1E, 0x92, 0x0D, 32, 64, 4, 64],
                [' ATmega8', 0x1E, 0x93, 0x07, 32, 128, 4, 128],
                [' ATmega8A', 0x1E, 0x93, 0x07, 32, 128, 4, 128],
                [' ATmega8L', 0x1E, 0x93, 0x07, 32, 128, 4, 128],
                [' ATmega16', 0x1E, 0x94, 0x03, 64, 128, 4, 128],
                [' ATmega16A', 0x1E, 0x94, 0x03, 64, 128, 4, 128],
                [' ATmega16U4', 0x1E, 0x94, 0x88, 64, 128, 4, 128],
                [' ATmega32U4', 0x1E, 0x95, 0x87, 64, 256, 4, 256],
                [' ATmega128', 0x1E, 0x97, 0x02, 128, 512, 8, 512],
                [' ATmega128A', 0x1E, 0x97, 0x02, 128, 512, 8, 512],
                [' ATmega128L', 0x1E, 0x97, 0x02, 128, 512, 8, 512],
                [' ATmega48V', 0x1E, 0x92, 0x05, 32, 64, 4, 64],
                [' ATmega88V', 0x1E, 0x93, 0x0A, 32, 128, 4, 128],
                [' ATmega168V', 0x1E, 0x94, 0x06, 64, 128, 4, 128],
                [' ATmega328P', 0x1E, 0x95, 0x0F, 64, 256, 4, 256],
                ['ATtiny88', 0x1E, 0x93, 0x11, 32, 128, 4, 16],
                ]

flash_page_size = AVR_mem_size[0][4]
flash_page_number = AVR_mem_size[0][5]
eeprom_page_size = AVR_mem_size[0][6]
eeprom_page_number = AVR_mem_size[0][7]
#=================================== MAIN WINDOW =======================================================================
window = Tk()
window.config(width=600, height=400, bg='light blue')
window.title("AVR loader")
#window.iconbitmap('icon.ico')

# ===================== MAIN WINDOW =====================================================================================
label_programer = Label(window, text="Programer:", fg="blue")
label_programer.place(x=5, y=5)

label_port = Label(window, text="Port:", fg="blue")
label_port.place(x=200, y=5)
label_selected_port = Label(window, text="Nics kiválasztott PORT")
label_selected_port.place(x=200, y=30)
def Update_label_port():
    if programer.get() == "AVRserial":
        if sellected_port.get() == "":
            label_selected_port.config(text="Nics kiválasztott PORT")
        else:
            label_selected_port.config(text=sellected_port.get())
    else:
        label_selected_port.config(text="USB")

label_microcontroller = Label(window, text="Microcontroller:", fg="blue")
label_microcontroller.place(x=400, y=5)

#=========================================== LOAD SCREEN ===============================================================
def Open_load_window(name, text):
    global Load_window, load_label, pb
    Load_window = Toplevel(window)
    Load_window.title(name)
    Load_window.geometry("300x100")
    #label
    load_label = Label( Load_window, text=text, justify=CENTER)
    load_label.place(x=150, y= 25, anchor = 'center')
    # progressbar
    pb = ttk.Progressbar(
        Load_window,
        orient='horizontal',
        mode='determinate',
        length=200
    )
    # place the progressbar
    pb.place(x=50, y=50)
    pb['value'] = Load_status
    window.update_idletasks()
    Load_window.update()
def Update_load_window():
    global pb
    pb['value'] = USBasp.load_percentage
    Load_window.update()
    Load_window.update_idletasks()
def Change_text_load_window(text):
    load_label.config(text = text)
def Delete_load_window():
    Load_window.destroy()


def task():
    try:
        Update_load_window()
    except:
        pass
    root.after(10, task)


#========================================== Error window ===============================================================
def Open_message_window(name, text, color):
    global message_window, message_label
    message_window = Toplevel(window)
    message_window.title(name)
    message_window.geometry("300x100")
    #label
    message_label = Label(message_window, text=text, fg=color, justify=CENTER)
    message_label.place(x=150, y= 30, anchor = 'center')
    button_message = Button(message_window, text="OK", command=message_window.destroy)
    button_message.place(x=150, y=70, anchor = 'center')
def Change_text_message_window(text):
    message_label.config(text = text)
def Delete_message_window():
    message_window.destroy()

#================================== SERIAL =============================================================================
sellected_port = StringVar()
ports_list = []

def Sellect_port():
    Update_label_port()

def Find_ports():
    global ports_list, sellected_port
    for a in ports_list:
        port_menu.delete(a)
    ports_list = []
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        ports_list.append(port)
        port_menu.add_radiobutton(label=port, variable=sellected_port, value=port, command=Sellect_port)

#================================= FILE HANDELING ======================================================================
line_lenght = 0x20

flash = []
flash_filename = {}
def Load_flash():
    global flash, flash_filename
    flash_filename = Get_open_filename()
    flash = Hex_to_list(Read_from_file(flash_filename))
    v.set("flash")
    Mylist_sellect()

def Save_flash():
    Save_to_file(Lines_to_hex(List_to_lines(flash, line_lenght), line_lenght), flash_filename)
def Save_as_flash():
    Save_to_file(Lines_to_hex(List_to_lines(flash, line_lenght), line_lenght), Get_save_filename())

eeprom = []
eeprom_filename = {}
def Load_eeprom():
    global eeprom, eeprom_filename
    eeprom_filename = Get_open_filename()
    eeprom = Hex_to_list(Read_from_file(eeprom_filename))
    v.set("eeprom")
    Mylist_sellect()
def Save_eeprom():
    Save_to_file(Lines_to_hex(List_to_lines(flash, line_lenght), line_lenght), eeprom_filename)
def Save_as_eeprom():
    Save_to_file(Lines_to_hex(List_to_lines(eeprom, line_lenght), line_lenght), Get_save_filename())

mcu_flash = []
def Save_mcu_flash():
    Save_to_file(Lines_to_hex(List_to_lines(mcu_flash, line_lenght), line_lenght))

mcu_eeprom = []
def Save_mcu_eeprom():
    Save_to_file(Lines_to_hex(List_to_lines(mcu_eeprom, line_lenght), line_lenght))

#================================= Target kommunikáció =================================================================
avr_bytes = []
def Read_fuse_bytes():
    global programer, avr_bytes
    avr_bytes = []
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        avr_bytes.append(AVRserial.Read_Lock_bits())
        for a in AVRserial.Read_Signature_byte():
            avr_bytes.append(a)
        avr_bytes.append(AVRserial.Read_Fuse_bits())
        avr_bytes.append(AVRserial.Read_Fuse_high_bits())
        avr_bytes.append(AVRserial.Read_extended_Fuse_bits())
        avr_bytes.append(AVRserial.Read_calibration_byte())
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        avr_bytes.append(USBasp.Read_Lock_bits())
        for a in USBasp.Read_Signature_byte():
            avr_bytes.append(a)
        avr_bytes.append(USBasp.Read_Fuse_bits())
        avr_bytes.append(USBasp.Read_Fuse_high_bits())
        avr_bytes.append(USBasp.Read_extended_Fuse_bits())
        avr_bytes.append(USBasp.Read_calibration_byte())
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        avr_bytes.append(USBtinyASP.Read_Lock_bits())
        for a in USBtinyASP.Read_Signature_byte():
            avr_bytes.append(a)
        avr_bytes.append(USBtinyASP.Read_Fuse_bits())
        avr_bytes.append(USBtinyASP.Read_Fuse_high_bits())
        avr_bytes.append(USBtinyASP.Read_extended_Fuse_bits())
        avr_bytes.append(USBtinyASP.Read_calibration_byte())
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    v.set("fuse/signature bits")
    Mylist_sellect()

def Dettect_AVR():
    global programer, AVR_mem_size, MCU
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        a = AVRserial.Read_Signature_byte()
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        a = USBasp.Read_Signature_byte()
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        a = USBtinyASP.Read_Signature_byte()
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    for mcu in AVR_mem_size:
        if (mcu[1] == a[0]) and (mcu[2] == a[1]) and (mcu[3] == a[2]):
            MCU.set(mcu[0])
            MCU_changed(a)
            break

def Errase():
    global programer
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        AVRserial.AVR_Errase()
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        USBasp.Errase()
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        USBtinyASP.Errase()
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass

def Read_Flash():
    global programer, flash_page_size, flash_page_number, mcu_flash
    Open_load_window(" ", "Reading Flash ...")
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        mcu_flash = AVRserial.Read_Flash(flash_page_number, flash_page_size)
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        mcu_flash = USBasp.Read_Flash(flash_page_number, flash_page_size)
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        mcu_flash = USBtinyASP.Read_Flash(flash_page_number, flash_page_size)
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    v.set("target flash")
    Mylist_sellect()
    Delete_load_window()

def Read_Flas_Verify():
    global programer, flash_page_size, flash_page_number, mcu_flash, flash
    Open_load_window(" ", "Reading Flash ...")
    words = List_to_lines(flash, 2)
    lines = List_to_lines(words, flash_page_size)
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        mcu_flash = AVRserial.Read_Flash(len(lines), flash_page_size)
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        mcu_flash = USBasp.Read_Flash(len(lines), flash_page_size)
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        mcu_flash = USBtinyASP.Read_Flash(len(lines), flash_page_size)
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    v.set("target flash")
    Mylist_sellect()
    Delete_load_window()

def Write_Flash():
    global programer, flash_page_size, flash_page_number, flash
    Open_load_window(" ", "Writeing Flash ...")
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        AVRserial.AVR_Errase()
        words = List_to_lines(flash, 2)
        lines = List_to_lines(words, flash_page_size)
        AVRserial.Write_Flash(lines, flash_page_size)
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        USBasp.Errase()
        words = List_to_lines(flash, 2)
        lines = List_to_lines(words, flash_page_size)
        USBasp.Write_Flash(lines, flash_page_size)
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        USBtinyASP.Errase()
        words = List_to_lines(flash, 2)
        lines = List_to_lines(words, flash_page_size)
        USBtinyASP.Write_Flash(lines, flash_page_size)
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    Delete_load_window()

def Write_and_Verify_Flash():
    Write_Flash()
    Verify_Flash()

def Read_EEPROM():
    global programer, eeprom_page_size, eeprom_page_number, mcu_eeprom
    Open_load_window(" ", "Reading EEPROM ...")
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        mcu_eeprom = AVRserial.Read_EEPROM(eeprom_page_number, eeprom_page_size)
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        mcu_eeprom = USBasp.Read_EEPROM(eeprom_page_number, eeprom_page_size)
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        mcu_eeprom = USBtinyASP.Read_EEPROM(eeprom_page_number, eeprom_page_size)
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    v.set("target eeprom")
    Mylist_sellect()
    Delete_load_window()

def Write_EEPROM():
    global programer, eeprom_page_size, eeprom_page_number, eeprom
    Open_load_window(" ", "Writeing EEPROM ...")
    if programer.get() == "AVRserial":
        AVRserial.AVR_Connect(sellected_port.get())
        AVRserial.Write_EEPROM(eeprom)
        AVRserial.AVR_Disconnect()
    elif programer.get() == "USBasp":
        USBasp.Connect()
        USBasp.Write_EEPROM(eeprom)
        USBasp.Disconnect()
    elif programer.get() == "USBthinyASP":
        USBtinyASP.Connect()
        USBtinyASP.Write_EEPROM(eeprom)
        USBtinyASP.Disconnect()
    elif programer.get() == "Arduino bootloader":
        pass
    Delete_load_window()

def Write_and_Verify_EEPROM():
    Write_EEPROM()
    Verify_EEPROM()

def Verify_Flash():
    global flash, mcu_flash
    Read_Flas_Verify()
    for i, word in enumerate(flash):
        if flash[i] != mcu_flash[i]:
            Open_message_window("Verifying Flash", "Flash not verified", 'RED')
            return()
    Open_message_window("Verifying Flash", "Flash verified", 'GREEN')

def Verify_EEPROM():
    global eeprom, mcu_eeprom
    Read_EEPROM()
    for i, word in enumerate(eeprom):
        if eeprom[i] != mcu_eeprom[i]:
            Open_message_window("Verifying EEPROM", "EEPROM not verified", 'RED')
            return()
    Open_message_window("Verifying EEPROM", "EEPROM verified", 'GREEN')

#================================= MENU ================================================================================
my_menu = Menu(window)
window.config(menu=my_menu)

file_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load Flash File", command=Load_flash)
file_menu.add_command(label="Save Flash File", command=Save_flash)
file_menu.add_command(label="Save As Flash File", command=Save_as_flash)
file_menu.add_separator()
file_menu.add_command(label="Load EEPROM File", command=Load_eeprom)
file_menu.add_command(label="Save EEPROM File", command=Save_eeprom)
file_menu.add_command(label="Save As EEPROM File", command=Save_as_eeprom)
file_menu.add_separator()
file_menu.add_command(label="Save Target Flash Memory", command=Save_mcu_flash)
file_menu.add_command(label="Save Target EEPROM Memory", command=Save_mcu_eeprom)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

view_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="View", menu=view_menu)
view_menu.add_command(label="Flash File", command=place_holder)
view_menu.add_command(label="Target Flash Memory", command=place_holder)
view_menu.add_separator()
view_menu.add_command(label="EEPROM File", command=place_holder)
view_menu.add_command(label="Target EEPROM Memory", command=place_holder)
view_menu.add_separator()
view_menu.add_command(label="View fuse bytes", command=place_holder)

port_menu = Menu(my_menu, tearoff=0, postcommand=Find_ports)
my_menu.add_cascade(label="Sellect Port", menu=port_menu)

target_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Target", menu=target_menu)
target_menu.add_command(label="Read fuse bytes", command=Read_fuse_bytes)
target_menu.add_command(label="Dettect AVR", command=Dettect_AVR)
target_menu.add_separator()
target_menu.add_command(label="Errase", command=Errase)
target_menu.add_separator()
target_menu.add_command(label="Read Flash", command=Read_Flash)
target_menu.add_command(label="Write Flash", command=Write_Flash)
target_menu.add_command(label="Write and Verify Flash", command=Write_and_Verify_Flash)
target_menu.add_separator()
target_menu.add_command(label="Read EEPROM", command=Read_EEPROM)
target_menu.add_command(label="Write EEPROM", command=Write_EEPROM)
target_menu.add_command(label="Write and Verify EEPROM", command=Write_and_Verify_EEPROM)
target_menu.add_separator()
target_menu.add_command(label="Verify Flash", command=Verify_Flash)
target_menu.add_command(label="Verify EEPROM", command=Verify_EEPROM)

settings_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Settings", menu=settings_menu)

help_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Help", menu=help_menu)



#============================================ SELLECT MICROCONTROLLER ==================================================
# Combobox creation
MCU = StringVar()
MCUchoosen = ttk.Combobox(window, width=27, textvariable=MCU)

# Adding combobox drop down list
tmp = []
for x in AVR_mem_size:
    tmp.append(x[0])
MCUchoosen['values'] = tmp
MCU.set(AVR_mem_size[0][0])

MCUchoosen['state'] = 'readonly'
MCUchoosen.place(x=400, y=30)

def MCU_changed(a):
    global flash_page_size, flash_page_number, eeprom_page_size, eeprom_page_number
    for x in AVR_mem_size:
        if x[0] == MCU.get():
            flash_page_size = x[4]
            flash_page_number = x[5]
            eeprom_page_size = x[6]
            eeprom_page_number = x[7]
MCUchoosen.bind('<<ComboboxSelected>>', MCU_changed)

# ========================= SELLECT PROGRAMER ===========================================================================
# Dropdown menu options
options = [
    "AVRserial",
    "USBasp",
    "USBthinyASP",
    "Arduino bootloader",
]
# datatype of menu text
programer = StringVar()
# initial menu text
programer.set("AVRserial")

# menu function
def Programer_changed(programer):
    if programer == "Arduino bootloader":
        # Adding combobox drop down list
        MCUchoosen['values'] = (' Arduino Uno',
                                ' Arduino Nano'
                                )
        MCU.set(' Arduino Uno')
    else:
        tmp = []
        for x in AVR_mem_size:
            tmp.append(x[0])
        MCUchoosen['values'] = tmp
        MCU.set(AVR_mem_size[0][0])
    Update_label_port()
# Create Dropdown menu
drop = OptionMenu(window, programer, *options, command=Programer_changed)
drop.place(x=5, y=30)

#=========================================== Data display ==============================================================

scrollbar = Scrollbar(window, orient="vertical")
scrollbar.place(x=570, y=123, height=220)

mylist = Listbox(window, yscrollcommand=scrollbar.set)
mylist.configure(font='TkFixedFont')
mylist.place(x=10, y=143, height=200, width=560 )

scrollbar.config(command=mylist.yview)

mylist_top = Listbox(window,)
mylist_top.configure(font='TkFixedFont')
mylist_top.place(x=10, y=123, height=20, width=560 )


def Mylist_fill_flash(data):
    lines = List_to_lines(data, 0x10)
    mylist_top.delete(0, mylist.size())
    mylist_top.insert(END, "       00/08  01/09  02/0A  03/0B  04/0C  05/0D  06/0E  07/0F")
    mylist.delete(0, mylist.size())
    for i, line in enumerate(lines):
        words = List_to_lines(line, 0x2)
        printl = ((str(hex(i*0x8))[2:]).zfill(4)).upper()
        for word in words:
            printl = printl + "   " + (str(hex(word[0]))[2:].zfill(2) + str(hex(word[1]))[2:].zfill(2)).upper()
        mylist.insert(END ,printl)
        mylist.insert(END, "")

def Mylist_fill_eeprom(data):
    lines = List_to_lines(data, 0x10)
    mylist_top.delete(0, mylist.size())
    mylist_top.insert(END, "      00  01  02  03  04  05  06  07  08  09  0A  0B  0C  0D  0E  0F")
    mylist.delete(0, mylist.size())
    for i, line in enumerate(lines):
        printl = ((str(hex(i*0x10))[2:]).zfill(4)).upper()
        for byte in line:
            printl = printl + "  " + ((str(hex(byte))[2:]).zfill(2)).upper()
        mylist.insert(END ,printl)
        mylist.insert(END, "")

def Mylist_fill_bits(data):
    mylist_top.delete(0, mylist.size())
    mylist.delete(0, mylist.size())
    labels = ["lock bits:", "signature byte 0x00:", "signature byte 0x01:", "signature byte 0x02:", "signature byte 0x03:", "signature byte 0x04:", "fuse bits:", "fuse high bits:", "extended fuse bits:", "calibration byte:"]
    for i in range(len(data)):
        printl = labels[i] + "    " + ((str(hex(data[i]))[2:]).zfill(2)).upper()
        mylist.insert(END, printl)

def Mylist_sellect():
    global flash, mcu_flash, eeprom, mcu_eeprom
    if v.get() == "flash":
        Mylist_fill_flash(flash)
    elif v.get() == "eeprom":
        Mylist_fill_eeprom(eeprom)
    elif v.get() == "target flash":
        Mylist_fill_flash(mcu_flash)
    elif v.get() == "target eeprom":
        Mylist_fill_eeprom(mcu_eeprom)
    elif v.get() == "fuse/signature bits":
        Mylist_fill_bits(avr_bytes)

v = StringVar(window, "1")

values = {"Flash" : "flash",
          "EEPROM" : "eeprom",
          "Target Flash" : "target flash",
          "Target EEPROM" : "target eeprom",
          "Fuse bits" : "fuse/signature bits"}

for i, (text, value) in enumerate(values.items()):
    Radiobutton(window, text = text, font=('lucida', 9, 'bold'), variable = v,
                value = value, indicator = 0,
                background = "light gray", command=Mylist_sellect).place(x=(10+i*100), y=100, width=100)


#=============================== MAIN LOOP =============================================================================
window.mainloop()
