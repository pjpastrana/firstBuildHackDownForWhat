import traceback

##########################################################
# Define the values returned by the barcode reader
##########################################################

barcmd = {}
barcmd['0']="27"
barcmd['1']="1e"
barcmd['2']="1f"
barcmd['3']="20"
barcmd['4']="21"
barcmd['5']="22"
barcmd['6']="23"
barcmd['7']="24"
barcmd['8']="25"
barcmd['9']="26"

	
def get_barcode(dev = "/dev/hidraw0"):
    
    hiddev = open(dev, "rb")

    looping = True
    barcode = ""

    i = 0
    twelve = 0
    while looping:
        usbraw = hiddev.read(16)
        usbhex = usbraw.encode("hex")
        if i % 6 == 0:
            usbhex = " ".join(usbhex[24:26]).replace(' ',"")
            twelve += 1
            for key in barcmd:
                if barcmd[key] == usbhex:
                    barcode += key
                    break
        if twelve == 12:
            break
        i += 1
    hiddev.close()
    print "barcode " + barcode
    return barcode

##########
# MAIN 
##########
if __name__ == "__main__":
    try:
        print get_barcode("/dev/input/event2")
        
    except KeyboardInterrupt:
        # Exit on CTRL-C
        print "\nExiting...\n"

    except:
        # An error occured
        print "\nException:"
        traceback.print_exc()

	

