


from tkinter import filedialog
import os

#================================= LOAD ================================================================================

#---------- kiovasás fájlból -------------------------------------------------------------------------------------------
def Get_open_filename():
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Hex files", "*.hex*"),
                                                                                            ("Text files", "*.txt*"),
                                                                                            ("all files", "*.*"),
                                                                                            ("EEPROM files", "*.eep*")))
    return(filename)

def Read_from_file(filename):
    my_file = open(filename, "r")
    content = my_file.read()
    content = content.split('\n')     #hex file sorokra osztása
    return(content)

#--------------------hex file változókra osztása  ----------------------------------------------------------------------
def Hex_to_list(content_HEX):
    content_LIST = []
    for line_HEX in content_HEX:
        if len(line_HEX) != 0:   #checking if line not empty
            if line_HEX[0] != ":":
                return (1)      #missing ":" error
            else:
                if line_HEX[7:9] == "00":   #checking if Record type is Data(0x00)
                    while len(content_LIST) < int(line_HEX[3:7], 16): #filling empty spaces with 0xFF
                        content_LIST.append(0xFF)
                    for i in range(int(line_HEX[1:3], 16)):      #save data bytes
                        content_LIST.append(int(line_HEX[9+2*i:11+2*i], 16))
                    b = int(line_HEX[1:3], 16)            #calculate checksum
                    b = b + int(line_HEX[3:5], 16)
                    b = b + int(line_HEX[5:7], 16)
                    b = b + int(line_HEX[7:9], 16)
                    for i in range(int(line_HEX[1:3], 16)):
                        b = b + int(line_HEX[9+2*i:11+2*i], 16)
                    if int(line_HEX[9+2*int(line_HEX[1:3], 16):11+2*int(line_HEX[1:3], 16)], 16) != ((b^0xFF)+1)%0x100 :
                        return(2)      #checksum error
    return(content_LIST)

#============================================= SAVE ====================================================================

#-------------------------------- változók egyesítése hex file sorokká -------------------------------------------------
def List_to_lines(content_LIST, line_lenght):
    lines = []
    for i, a in enumerate(content_LIST):
        if i%line_lenght == 0:
            lines.append([])
        lines[int(i/line_lenght)].append(a)
    return(lines)

def Lines_to_hex(lines, line_lenght):
    content_HEX = []
    for i, a in enumerate(lines):
        adress = line_lenght * i
        data_bytes = []
        j = 0
        while j<len(a) and a[j]==0xFF:
            adress = adress + 1
            j = j+1
        while j<len(a):
            data_bytes.append(a[j])
            j = j+1
        j = len(data_bytes) - 1
        while j>=0 and data_bytes[j]==0xFF:
            data_bytes.pop()
            j = j-1
        character_count = len(data_bytes)
        checksum = (((character_count + int(adress/0x100) + adress%0x100 + sum(data_bytes))^0xFF)+1)%0x100
        content_HEX.append(":")
        content_HEX[i] = content_HEX[i] + (str(hex(character_count))[2:]).zfill(2) + (str(hex(adress))[2:]).zfill(4) + "00"
        for b in data_bytes:
            content_HEX[i] = content_HEX[i] + (str(hex(b))[2:]).zfill(2)
        content_HEX[i] = content_HEX[i] + (str(hex(checksum))[2:]).zfill(2)
    content_HEX.append(':00000001ff')
    for i, a in enumerate(content_HEX):
        content_HEX[i] = a.upper()
    return(content_HEX)

def Get_save_filename():
    # ---------------- fájl kezelő ablak -------------------------------------------------------------------------------
    filename = filedialog.asksaveasfilename(initialdir="/", title="Save File", filetypes=(("Hex files", "*.hex*"),
                                                                 ("Text files", "*.txt*"), ("all files", "*.*")))
    if filename[-4:] != ".hex":
        filename = filename + ".hex"
    return(filename)

def Save_to_file(content_HEX, filename):

    my_file = open(filename, "w")
    # ----------------- hex fájl kiírása fájlba ------------------------------------------------------------------------
    my_file.seek(0)
    my_file.truncate()
    for i in content_HEX:
        my_file.write(i + "\n")
    my_file.close()