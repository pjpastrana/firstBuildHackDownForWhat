from multiprocessing import Pool
from mcr12 import *
from subprocess import call
import os

def main():
    pool = Pool(processes=2)
    while True:
        pool.apply_async(get_barcode, callback=add_item)
        pool.apply_async(check_weight_change, callback=remove_item)
        #barcode = result.get(timeout=1)
        #print barcode
        #scan_has_ocurred()
        # pool.apply_async(scan_has_ocurred, callback = add_item)
        # pool.close()
        # pool.join()


# def scan_has_ocurred():
#     #pool = Pool(1)
#     pool.apply_async(get_barcode, callback = add_item)
#     #pool.close()
#     pool.join()
#     #return get_barcode("/dev/input/event2")

def check_weight_change():
    return

def add_item(barcode):
    print "adding item"
    print barcode
    #status = call("/tmp/smart_shelf" + " a", shell=False)
    #print status
    os.system("/tmp/smart_shelf a")

def remove_item(result):
    print "removing item"
    print result
    
# start process
if __name__ == "__main__":
    main()

# root@smartShelf:~# /tmp/smart_shelf 
# Invalid parameters
# root@smartShelf:~# /tmp/smart_shelf w 1 2 3 4
# 10.000000
# root@smartShelf:~# /tmp/smart_shelf q 1 2 3 4
# 2
# root@smartShelf:~# /tmp/smart_shelf f 1 2 3 4
# 1.378500 0.793389 0.741862 0.514363
# root@smartShelf:~# /tmp/smart_shelf a
# 139 138 142 151
# root@smartShelf:~# /tmp/smart_shelf r 1 2 3 4
# 3304.290039 1650.530029 1099.276733 823.650024
# root@smartShelf:~# 
